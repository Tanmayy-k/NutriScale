# -*- coding: utf-8 -*-
"""prototype.py — NutriScale TA2 Core Prototype"""
import os, sys, json, time, re, sqlite3
from typing import TypedDict, Optional
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, ToolMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
sys.path.insert(0, os.path.dirname(__file__))
from ta2_tools import scale_recipe, estimate_calories, retrieve_nutrition_info, rag_scale_and_estimate

MODEL, MAX_HOPS, DB = "qwen2.5:3b", 10, os.path.join(os.path.dirname(__file__), "memory.db")
UNSAFE = ["cure", "treat", "diagnose", "medic", "prescription", "disease"]
ALIASES = {"dairy": ["milk", "cheese", "butter", "cream", "yogurt"], "milk": ["dairy", "cheese", "butter"],
           "gluten": ["wheat", "barley", "rye", "bread", "flour"], "wheat": ["gluten", "bread", "flour"],
           "peanut": ["peanuts", "groundnut", "peanut butter"], "groundnut": ["peanut", "peanuts"]}
llm, short_mem = ChatOllama(model=MODEL, temperature=0), MemorySaver()

# ── Long-term SQLite memory ───────────────────────────────────────────────────
def _db(q, p=()): c=sqlite3.connect(DB); c.execute(q,p); c.commit(); c.close()
_db("CREATE TABLE IF NOT EXISTS prefs(user_id TEXT, key TEXT, value TEXT, PRIMARY KEY(user_id,key))")
_db("CREATE TABLE IF NOT EXISTS allergies(user_id TEXT, allergen TEXT, PRIMARY KEY(user_id, allergen))")
def ltm_save(uid, k, v): _db("INSERT OR REPLACE INTO prefs VALUES(?,?,?)",(uid,k,v))
def ltm_load(uid): c=sqlite3.connect(DB); r=c.execute("SELECT key,value FROM prefs WHERE user_id=?",(uid,)).fetchall(); c.close(); return dict(r)
def ltm_save_allergy(uid, a): _db("INSERT OR IGNORE INTO allergies VALUES(?,?)", (uid, a.lower().strip()))
def ltm_load_allergies(uid): c=sqlite3.connect(DB); r=c.execute("SELECT allergen FROM allergies WHERE user_id=?", (uid,)).fetchall(); c.close(); return [x[0].lower() for x in r]

# ── Sub-agents ────────────────────────────────────────────────────────────────
RECIPE_PROMPT = ("You are Recipe Agent. When asked to scale and estimate calories: "
                 "1. Call scale_recipe FIRST. Do NOT call estimate_calories yet. "
                 "2. Wait for scale_recipe result. "
                 "3. Call estimate_calories using the SCALED ingredient amount from scale_recipe. "
                 "Never call estimate_calories using the original amount.")
recipe_agent = create_react_agent(llm, [scale_recipe, estimate_calories, rag_scale_and_estimate], checkpointer=short_mem, prompt=RECIPE_PROMPT)
nutrition_agent = create_react_agent(llm, [retrieve_nutrition_info], checkpointer=short_mem, prompt="You are Nutrition Agent. Use retrieve_nutrition_info. Cite source.")

class NS(TypedDict):
    user_id: str; thread_id: str; request: str; prefs: dict; allergies: list
    guard_ok: Optional[bool]; guard_reason: Optional[str]; route: Optional[str]; answer: Optional[str]; trace: list

# ── Guards & Supervisor ───────────────────────────────────────────────────────
def guard_node(s: NS) -> NS:
    req, tr = s["request"], s["trace"][:]
    tr.append({"node":"guard","event":"checking","request":req})
    for kw in UNSAFE:
        if kw in req.lower():
            r=f"Blocked: contains medical keyword '{kw}'."
            return {**s,"guard_ok":False,"guard_reason":r,"trace":tr+[{"node":"guard","decision":"BLOCKED","reason":r}]}
    negs=[float(x) for x in re.findall(r"-\d+(?:\.\d+)?",req)]
    if negs:
        r=f"Blocked: negative number(s) {negs} in request."
        return {**s,"guard_ok":False,"guard_reason":r,"trace":tr+[{"node":"guard","decision":"BLOCKED","reason":r}]}
    return {**s,"guard_ok":True,"trace":tr+[{"node":"guard","decision":"PASS"}]}

def allergen_guard_node(s: NS) -> NS:
    req, tr, al = s["request"], s["trace"][:], s.get("allergies") or []
    words = [w.strip(".,!?;:\"'()[]{}").lower() for w in req.split()]
    if any(k in words for k in ["unknown", "mystery", "unnamed"]):
        r = "UNKNOWN: ingredient is ambiguous, blocked pending clarification."
        return {**s, "guard_ok": False, "guard_reason": r, "trace": tr + [{"node": "allergen_guard", "decision": "BLOCKED", "reason": r}]}
    req_lower = req.lower()
    for a in al:
        for t in [a.lower()] + ALIASES.get(a.lower(), []):
            if re.search(r'\b' + re.escape(t) + r'\b', req_lower):
                r = f"Allergen match: {a} (matched '{t}') found in request."
                return {**s, "guard_ok": False, "guard_reason": r, "trace": tr + [{"node": "allergen_guard", "decision": "BLOCKED", "reason": r}]}
    return {**s, "guard_ok": True, "trace": tr + [{"node": "allergen_guard", "decision": "PASS"}]}

def supervisor_node(s: NS) -> NS:
    req = s["request"].lower()
    route = "nutrition" if ("what" in req or ("calori" in req and "scale" not in req and "serv" not in req)) else "recipe"
    return {**s,"route":route,"trace":s["trace"]+[{"node":"supervisor","route":route}]}

# ── Agent Runner & Graph ──────────────────────────────────────────────────────
def _run(agent, s: NS, name: str) -> NS:
    cfg = {"configurable":{"thread_id":s["thread_id"]},"recursion_limit":MAX_HOPS}
    ctx = f"\nUser preferences: {json.dumps(s['prefs'])}" if s['prefs'] else ""
    t0 = time.time(); res = agent.invoke({"messages":[HumanMessage(content=s["request"]+ctx)]}, config=cfg); ela = round(time.time()-t0,2)
    msgs = res.get("messages",[])
    ans = next((m.content for m in reversed(msgs) if hasattr(m,"content") and m.content and not getattr(m,"tool_calls",None)),"No answer.")
    for m in msgs:
        if isinstance(m, ToolMessage) and isinstance(m.content, str) and m.content.startswith("Estimated calories:") and m.content not in ans:
            ans += f"\n[Tool output] {m.content}"
    return {**s,"answer":ans,"trace":s["trace"]+[{"node":name,"elapsed_s":ela,"answer_preview":ans[:120]}]}

def recipe_node(s:NS)->NS: return _run(recipe_agent, s, "recipe_agent")
def nutrition_node(s:NS)->NS: return _run(nutrition_agent, s, "nutrition_agent")

def _graph():
    g = StateGraph(NS)
    for n, f in [("guard",guard_node), ("allergen_guard",allergen_guard_node), ("supervisor",supervisor_node), ("recipe",recipe_node), ("nutrition",nutrition_node)]:
        g.add_node(n, f)
    g.set_entry_point("guard")
    g.add_conditional_edges("guard", lambda s:"allergen_guard" if s["guard_ok"] else END)
    g.add_conditional_edges("allergen_guard", lambda s:"supervisor" if s["guard_ok"] else END)
    g.add_conditional_edges("supervisor", lambda s:s["route"], {"recipe":"recipe", "nutrition":"nutrition"})
    g.add_edge("recipe", END); g.add_edge("nutrition", END)
    return g.compile()

graph = _graph()

def run(request: str, user_id: str="default", thread_id: str="t1") -> dict:
    prefs, allergies = ltm_load(user_id), ltm_load_allergies(user_id)
    s: NS = {"user_id":user_id, "thread_id":thread_id, "request":request, "prefs":prefs, "allergies":allergies,
             "guard_ok":None, "guard_reason":None, "route":None, "answer":None, "trace":[]}
    final = graph.invoke(s, config={"recursion_limit":MAX_HOPS})
    if not final.get("guard_ok"): final["answer"] = f"Request blocked: {final.get('guard_reason','unknown')}"
    return final

if __name__=="__main__":
    r = run("Scale 200g rice from 4 to 8 servings, estimate calories at 1.3 kcal/g", user_id="demo", thread_id="smoke1")
    print("ANSWER:", r["answer"]); print("GUARD:", r["guard_ok"]); print("ROUTE:", r["route"])
