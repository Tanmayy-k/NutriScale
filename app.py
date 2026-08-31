# -*- coding: utf-8 -*-
"""
app.py — NutriScale Streamlit Application
==========================================
FIXED: All workflow/trace rendering now uses native Streamlit components only.
No custom HTML in the workflow, trace, or result sections.
Only the page-level CSS block and the hero banner use st.markdown(html).

AGENT LOGIC IS UNCHANGED:
  - ChatOllama(model="qwen2.5:3b", temperature=0)
  - create_agent() with both tools
  - Autonomous tool-calling chain
  - Trace extraction from messages list
"""

import json
import re
import streamlit as st
from langchain_ollama import ChatOllama
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage

from tools import scale_recipe, estimate_calories

# ─────────────────────────────────────────────────────────────────────────────
# Page config
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="NutriScale · Autonomous Nutrition Agent",
    page_icon="🥗",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────────────────────────────────────
# Minimal CSS — only global overrides that don't depend on custom class names
# injected via st.markdown(...). All component styling uses native Streamlit.
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
html, body, [data-testid="stAppViewContainer"] {
    background-color: #0e1117;
    color: #e0e0e0;
    font-family: 'Segoe UI', system-ui, sans-serif;
}
[data-testid="stHeader"]  { background: transparent; }
#MainMenu, footer         { visibility: hidden; }

[data-testid="block-container"] {
    max-width: 1060px;
    margin: 0 auto;
    padding-top: 0.5rem;
}

/* Input fields */
[data-testid="stNumberInput"] input,
[data-testid="stTextInput"]   input,
[data-testid="stTextArea"]    textarea {
    background: #0d1117 !important;
    border: 1px solid #30363d !important;
    border-radius: 7px !important;
    color: #e0e0e0 !important;
}

/* Primary button */
[data-testid="stButton"] > button[kind="primary"] {
    background: linear-gradient(135deg, #16a34a, #22c55e) !important;
    border: none !important;
    border-radius: 8px !important;
    font-size: 0.95rem !important;
    font-weight: 700 !important;
    color: #fff !important;
}

/* Divider */
hr { border-color: #21262d !important; }
</style>
""", unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════════════════════
# AGENT FACTORY  (unchanged)
# ═════════════════════════════════════════════════════════════════════════════

@st.cache_resource
def get_agent():
    llm = ChatOllama(model="qwen2.5:3b", temperature=0)
    system_prompt = (
        "You are NutriScale, an autonomous nutrition assistant. "
        "When a user asks you to scale a recipe and estimate calories, you MUST:\n"
        "  1. Call scale_recipe FIRST to get the scaled ingredient amount.\n"
        "  2. Call estimate_calories SECOND using the scaled amount from step 1.\n"
        "  3. Provide a clear final answer summarising both results.\n"
        "Always use both tools in sequence. Do not skip any tool."
    )
    return create_agent(
        model=llm,
        tools=[scale_recipe, estimate_calories],
        system_prompt=system_prompt,
    )


# ═════════════════════════════════════════════════════════════════════════════
# TRACE HELPERS  (unchanged logic)
# ═════════════════════════════════════════════════════════════════════════════

def _safe_json(obj) -> str:
    if isinstance(obj, dict):
        return json.dumps(obj, indent=2)
    return str(obj)


def extract_trace(messages: list) -> list[dict]:
    trace = []
    n = len(messages)
    for idx, msg in enumerate(messages):
        if isinstance(msg, HumanMessage):
            trace.append({"role": "user", "content": msg.content})
        elif isinstance(msg, AIMessage):
            is_last = (idx == n - 1)
            if msg.tool_calls:
                for tc in msg.tool_calls:
                    trace.append({
                        "role": "tool_call",
                        "tool_name": tc["name"],
                        "content": _safe_json(tc.get("args", {})),
                        "tool_call_id": tc.get("id", ""),
                    })
            elif is_last and msg.content:
                trace.append({"role": "final_answer", "content": msg.content})
            elif msg.content:
                trace.append({"role": "agent", "content": msg.content})
        elif isinstance(msg, ToolMessage):
            trace.append({
                "role": "tool_result",
                "tool_name": getattr(msg, "name", "tool"),
                "content": msg.content,
                "tool_call_id": getattr(msg, "tool_call_id", ""),
            })
    return trace


# ═════════════════════════════════════════════════════════════════════════════
# NATIVE STREAMLIT WORKFLOW RENDERER
# Zero custom HTML — uses only st.container, st.info, st.success,
# st.warning, st.code, st.write, st.divider, st.markdown (plain text only).
# ═════════════════════════════════════════════════════════════════════════════

_ROLE_EMOJI = {
    "user":         "🧑",
    "tool_call":    "🔧",
    "tool_result":  "📦",
    "final_answer": "🎯",
    "agent":        "🤖",
}

_ROLE_LABEL = {
    "user":         "USER REQUEST",
    "tool_call":    "TOOL CALL",
    "tool_result":  "TOOL RESULT",
    "final_answer": "FINAL ANSWER",
    "agent":        "AGENT",
}


def render_workflow_step(step: dict, connector: bool = True):
    """
    Render one agent workflow step using ONLY native Streamlit components.
    connector=True draws a visual arrow between steps.
    """
    role      = step["role"]
    emoji     = _ROLE_EMOJI.get(role, "•")
    label     = _ROLE_LABEL.get(role, role.upper())
    tool_name = step.get("tool_name", "")
    content   = step["content"]

    # ── Header label ─────────────────────────────────────────────────────────
    if tool_name:
        st.markdown(f"**{emoji} {label}** &nbsp;·&nbsp; `{tool_name}`")
    else:
        st.markdown(f"**{emoji} {label}**")

    # ── Content box using the appropriate native component ────────────────────
    if role == "user":
        st.info(content, icon="🧑")

    elif role == "tool_call":
        # Parse args JSON for clean display
        try:
            args = json.loads(content)
            lines = [f"  {k} = {v}" for k, v in args.items()]
            st.code("\n".join(lines), language="text")
        except Exception:
            st.code(content, language="text")

    elif role == "tool_result":
        st.success(content, icon="📦")

    elif role == "final_answer":
        st.success(content, icon="🎯")

    elif role == "agent":
        st.write(content)

    # ── Connector arrow ───────────────────────────────────────────────────────
    if connector:
        st.markdown("&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;⬇️", unsafe_allow_html=True)


def render_trace_card(step: dict):
    """Render one detailed trace entry using native Streamlit components."""
    role      = step["role"]
    emoji     = _ROLE_EMOJI.get(role, "•")
    label     = _ROLE_LABEL.get(role, role.upper())
    tool_name = step.get("tool_name", "")
    content   = step["content"]

    if tool_name:
        header = f"{emoji} {label} · {tool_name}"
    else:
        header = f"{emoji} {label}"

    with st.container(border=True):
        st.caption(header)
        if role in ("tool_call",):
            st.code(content, language="json")
        else:
            st.write(content)


# ═════════════════════════════════════════════════════════════════════════════
# HEADER
# ═════════════════════════════════════════════════════════════════════════════

col_logo, col_title = st.columns([1, 8], gap="small")
with col_logo:
    st.markdown("# 🥗")
with col_title:
    st.markdown("# NutriScale")
    st.markdown(
        "**Autonomous Recipe Scaling & Nutrition Estimation Agent**  \n"
        "Provide one natural-language request. The AI agent independently chains "
        "`scale_recipe` → `estimate_calories` with no hard-coded orchestration."
    )

st.divider()


# ═════════════════════════════════════════════════════════════════════════════
# RECIPE CONFIGURATION
# ═════════════════════════════════════════════════════════════════════════════

st.subheader("📝 Recipe Configuration")

col_a, col_b, col_c = st.columns([1, 1, 1.3], gap="medium")

with col_a:
    with st.container(border=True):
        st.markdown("**Servings**")
        servings_original = st.number_input(
            "Original Servings", min_value=1, value=4, step=1,
            help="How many servings the recipe currently makes.",
        )
        servings_target = st.number_input(
            "Target Servings", min_value=1, value=8, step=1,
            help="How many servings you want to make.",
        )

with col_b:
    with st.container(border=True):
        st.markdown("**Ingredient**")
        ingredient_name = st.text_input(
            "Ingredient Name", value="rice",
        )
        ingredient_amount = st.number_input(
            "Amount (original servings)", min_value=0.0, value=200.0, step=10.0,
        )

with col_c:
    with st.container(border=True):
        st.markdown("**Nutrition**")
        calories_per_unit = st.number_input(
            "Calories per Unit", min_value=0.0, value=1.3,
            step=0.1, format="%.2f",
            help="e.g. 1.3 kcal per gram of rice.",
        )
        if servings_original > 0:
            factor         = servings_target / servings_original
            preview_scaled = ingredient_amount * factor
            preview_kcal   = preview_scaled * calories_per_unit
            st.markdown("---")
            st.caption("Quick Preview")
            col_p1, col_p2, col_p3 = st.columns(3)
            col_p1.metric("Factor",   f"{factor:.2f}×")
            col_p2.metric("Scaled",   f"{preview_scaled:.1f} u")
            col_p3.metric("Est. kcal", f"{preview_kcal:.1f}")


# ═════════════════════════════════════════════════════════════════════════════
# NATURAL-LANGUAGE REQUEST
# ═════════════════════════════════════════════════════════════════════════════

st.divider()
st.subheader("💬 Tell NutriScale What You Need")
st.caption(
    "This single message is the only input the agent receives. "
    "It autonomously decides which tools to call and in what order."
)

default_question = (
    f"Scale {ingredient_amount} grams of {ingredient_name} from "
    f"{servings_original} servings to {servings_target} servings, "
    f"then estimate the calories if {ingredient_name} has "
    f"{calories_per_unit} calories per gram."
)

q_col, btn_col = st.columns([5, 1], gap="small")
with q_col:
    user_question = st.text_area(
        "Request",
        value=default_question,
        height=90,
        label_visibility="collapsed",
    )
with btn_col:
    st.write("")  # vertical spacing
    if st.button("✨ Example", use_container_width=True,
                 help="Load the classic demo example"):
        user_question = (
            "Scale 200 grams of rice from 4 servings to 8 servings, "
            "then estimate the calories if rice has 1.3 calories per gram."
        )
        st.info("Example loaded — click **Run NutriScale Agent** below.")

st.write("")
run_clicked = st.button(
    "🚀  Run NutriScale Agent",
    type="primary",
    use_container_width=True,
)


# ═════════════════════════════════════════════════════════════════════════════
# AGENT INVOCATION
# ═════════════════════════════════════════════════════════════════════════════

if run_clicked:
    # ── Friendly validation ───────────────────────────────────────────────────
    errors = []
    if not user_question.strip():
        errors.append("Please enter a request for the agent.")
    if servings_original <= 0:
        errors.append("Original Servings must be greater than 0.")
    if servings_target <= 0:
        errors.append("Target Servings must be greater than 0.")
    if ingredient_amount < 0:
        errors.append("Ingredient Amount cannot be negative.")
    if calories_per_unit < 0:
        errors.append("Calories per Unit cannot be negative.")

    if errors:
        for e in errors:
            st.error(f"⚠️  {e}")
        st.stop()

    agent = get_agent()

    with st.spinner("🤖  Agent is thinking and calling tools…"):
        try:
            result   = agent.invoke({"messages": [HumanMessage(content=user_question)]})
            messages = result.get("messages", [])
        except Exception as exc:
            st.error(f"Agent error: {exc}")
            st.stop()

    trace = extract_trace(messages)

    # ── Pull values from trace ────────────────────────────────────────────────
    scaled_display  = "—"
    calorie_display = "—"
    final_answer    = ""

    for step in trace:
        if step["role"] == "tool_result" and step.get("tool_name") == "scale_recipe":
            m = re.search(r"Scaled ingredient amount: ([0-9.]+)", step["content"])
            if m:
                scaled_display = m.group(1)
        if step["role"] == "tool_result" and step.get("tool_name") == "estimate_calories":
            m = re.search(r"Estimated calories: ([0-9.]+)", step["content"])
            if m:
                calorie_display = m.group(1)
        if step["role"] == "final_answer":
            final_answer = step["content"]

    # ─────────────────────────────────────────────────────────────────────────
    # RESULTS
    # ─────────────────────────────────────────────────────────────────────────
    st.divider()
    st.subheader("📊 Results")

    r1, r2 = st.columns(2, gap="medium")
    with r1:
        with st.container(border=True):
            st.metric(
                label="⚖️  Scaled Amount",
                value=f"{scaled_display} units",
                help=f"Ingredient amount scaled to {servings_target} servings.",
            )
    with r2:
        with st.container(border=True):
            st.metric(
                label="🔥  Estimated Calories",
                value=f"{calorie_display} kcal",
                help="Total calories for the scaled amount.",
            )

    if final_answer:
        st.success(f"🤖 **Agent says:** {final_answer}", icon="✅")

    # ─────────────────────────────────────────────────────────────────────────
    # AUTONOMOUS AGENT WORKFLOW  — pure native Streamlit, zero custom HTML
    # ─────────────────────────────────────────────────────────────────────────
    st.divider()
    st.subheader("🤖 Autonomous Agent Workflow")
    st.caption(
        "The agent received **one request** and independently selected & chained "
        "both tools. No Python code orchestrated the sequence."
    )

    visible_steps = [
        s for s in trace
        if s["role"] in ("user", "tool_call", "tool_result", "final_answer")
    ]

    for idx, step in enumerate(visible_steps):
        is_last = (idx == len(visible_steps) - 1)
        render_workflow_step(step, connector=not is_last)

    # ─────────────────────────────────────────────────────────────────────────
    # DETAILED TRACE EXPANDER
    # ─────────────────────────────────────────────────────────────────────────
    with st.expander("🔍 View Detailed Agent Trace", expanded=False):
        st.caption(
            "Full observable message chain — tool calls, arguments, results, "
            "and final response. Hidden chain-of-thought is excluded."
        )
        for step in trace:
            render_trace_card(step)

        with st.expander("🛠 Raw message objects (debugging)"):
            for i, msg in enumerate(messages):
                st.markdown(f"**Message {i} — `{type(msg).__name__}`**")
                st.code(str(msg), language="text")


# ═════════════════════════════════════════════════════════════════════════════
# FOOTER
# ═════════════════════════════════════════════════════════════════════════════

st.divider()
st.caption(
    "Powered by **Qwen2.5:3B** · **Ollama** · **LangChain** · **Streamlit**  \n"
    "NutriScale · Agentic AI Unit II · College Jury Project"
)
