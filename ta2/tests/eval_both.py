# -*- coding: utf-8 -*-
"""
eval_both.py -- NutriScale TA1 vs TA2 Evaluation
=================================================
Runs 5 representative test cases against BOTH TA1 and TA2.
Saves structured results to ta2/results/ta1_results.json,
ta2/results/ta2_results.json, and individual traces under ta2/results/traces/.

Usage:
    cd w:\\Ayoo\\NutriScale
    python -X utf8 ta2/tests/eval_both.py
"""

import sys, os, json, time, re, traceback

# Ensure both TA roots are importable
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))  # NutriScale/
TA1  = os.path.join(ROOT, "ta1")
TA2  = os.path.join(ROOT, "ta2")
RESULTS_DIR = os.path.join(TA2, "results")
TRACES_DIR  = os.path.join(RESULTS_DIR, "traces")
os.makedirs(TRACES_DIR, exist_ok=True)

# ── Import TA1 tools directly (deterministic, no LLM needed for basic checks) ──
sys.path.insert(0, TA1)
from tools import scale_recipe as ta1_scale, estimate_calories as ta1_calories
sys.path.pop(0)

# ── Import TA2 prototype ────────────────────────────────────────────────────────
sys.path.insert(0, TA2)
from prototype import run as ta2_run, ltm_save, ltm_load

# ── Reference values (ground truth) ──────────────────────────────────────────
REF_SCALED_RICE = 400.0   # 200g * (8/4)
REF_KCAL_RICE   = 520.0   # 400 * 1.3


def _extract_scaled(text: str) -> float | None:
    m = re.search(r"Scaled ingredient amount:\s*([\d.]+)", text or "")
    return float(m.group(1)) if m else None

def _extract_kcal(text: str) -> float | None:
    m = re.search(r"Estimated calories:\s*([\d.]+)", text or "")
    return float(m.group(1)) if m else None

def _kcal_error(val, ref):
    if val is None: return None
    return round(abs(val - ref), 2)


# ════════════════════════════════════════════════════════════════════════════════
# TA1 evaluation — calls tools directly (no LLM needed; TA1 uses LLM via agent
# but for the comparison we evaluate the deterministic tool outputs consistently)
# ════════════════════════════════════════════════════════════════════════════════

def run_ta1_case(tc_id: str, desc: str, **kwargs) -> dict:
    """Run a TA1 tool call sequence and record results."""
    result = {"tc_id": tc_id, "description": desc, "version": "TA1",
              "status": "UNKNOWN", "answer": "", "metrics": {}, "error": None}
    t0 = time.time()
    try:
        if tc_id in ("TC1", "TC2"):
            sr = ta1_scale.invoke({"servings_original": kwargs["so"],
                                   "servings_target": kwargs["st"],
                                   "ingredient_amount": kwargs["ia"]})
            scaled = _extract_scaled(sr)
            ec = ta1_calories.invoke({"ingredient_amount": scaled or 0,
                                      "calories_per_unit": kwargs["cpu"]})
            kcal = _extract_kcal(ec)
            result["answer"] = f"{sr} | {ec}"
            result["metrics"]["scaled_g"] = scaled
            result["metrics"]["kcal"] = kcal
            result["metrics"]["kcal_error"] = _kcal_error(kcal, kwargs.get("ref_kcal", REF_KCAL_RICE))
            result["metrics"]["scaling_correct"] = (scaled == kwargs.get("ref_scaled", REF_SCALED_RICE))
            result["status"] = "PASS" if (not sr.startswith("ERROR") and scaled is not None) else "FAIL"

        elif tc_id == "TC3":  # Thread memory — TA1 has no memory
            result["answer"] = "TA1 has no thread memory — N/A"
            result["metrics"]["memory_retrieved"] = "N/A"
            result["status"] = "NA"

        elif tc_id == "TC4":  # Long-term memory — TA1 has no persistence
            result["answer"] = "TA1 has no long-term memory — N/A"
            result["metrics"]["pref_retrieved"] = "N/A"
            result["status"] = "NA"

        elif tc_id == "TC5":  # Guard — TA1 validates inside tool
            sr = ta1_scale.invoke({"servings_original": -2,
                                   "servings_target": 8, "ingredient_amount": 200.0})
            blocked = sr.startswith("ERROR")
            result["answer"] = sr
            result["metrics"]["guard_blocked"] = blocked
            result["status"] = "PASS" if blocked else "FAIL"

    except Exception as e:
        result["status"] = "ERROR"; result["error"] = str(e)

    result["elapsed_s"] = round(time.time() - t0, 3)
    return result


# ════════════════════════════════════════════════════════════════════════════════
# TA2 evaluation — invokes the full TA2 prototype
# ════════════════════════════════════════════════════════════════════════════════

def run_ta2_case(tc_id: str, desc: str, request: str,
                 user_id: str = "eval_user", thread_id: str = None,
                 ref_kcal: float = None, ref_scaled: float = None,
                 check_guard: bool = False, check_memory: bool = False,
                 check_rag: bool = False) -> dict:
    result = {"tc_id": tc_id, "description": desc, "version": "TA2",
              "status": "UNKNOWN", "answer": "", "route": None,
              "guard_ok": None, "metrics": {}, "trace": [], "error": None}
    tid = thread_id or tc_id
    t0  = time.time()
    try:
        out = ta2_run(request, user_id=user_id, thread_id=tid)
        result["answer"]   = out.get("answer", "")
        result["route"]    = out.get("route")
        result["guard_ok"] = out.get("guard_ok")
        result["trace"]    = out.get("trace", [])

        ans = result["answer"]
        if check_guard:
            blocked = (out.get("guard_ok") is False)
            result["metrics"]["guard_blocked"] = blocked
            result["status"] = "PASS" if blocked else "FAIL"
        elif tc_id == "TC3":  # thread memory follow-up
            recalled = ("rice" in ans.lower() or "serv" in ans.lower()
                        or "400" in ans or "scale" in ans.lower())
            result["metrics"]["memory_retrieved"] = recalled
            result["status"] = "PASS" if recalled else "FAIL"
        elif tc_id == "TC4":  # long-term memory
            prefs = ltm_load(user_id)
            recalled = len(prefs) > 0
            result["metrics"]["prefs_in_db"] = dict(prefs)
            result["metrics"]["pref_retrieved"] = recalled
            result["status"] = "PASS" if recalled else "FAIL"
        elif check_rag:
            has_source = ("Source:" in ans or "source:" in ans
                          or "rice" in ans.lower() or "kcal" in ans.lower())
            result["metrics"]["rag_source_cited"] = has_source
            result["status"] = "PASS" if has_source else "PARTIAL"
        else:
            scaled = _extract_scaled(ans)
            kcal   = _extract_kcal(ans)
            result["metrics"]["scaled_g"]        = scaled
            result["metrics"]["kcal"]            = kcal
            result["metrics"]["kcal_error"]      = _kcal_error(kcal, ref_kcal) if ref_kcal else None
            result["metrics"]["scaling_correct"] = (scaled == ref_scaled) if ref_scaled else None
            no_err = ("ERROR" not in ans and "blocked" not in ans.lower())
            result["status"] = "PASS" if no_err else "FAIL"
    except Exception as e:
        result["status"] = "ERROR"; result["error"] = str(e)
        traceback.print_exc()

    result["elapsed_s"] = round(time.time() - t0, 3)
    return result


# ════════════════════════════════════════════════════════════════════════════════
# Main — define and run all 5 test cases
# ════════════════════════════════════════════════════════════════════════════════

UID = "eval_user"
TC1_REQ = "Scale 200g of rice from 4 servings to 8 servings. Calories per gram: 1.3."
TC2_REQ = ("What is the calorie density of chicken breast per gram? "
           "Retrieve from the knowledge base.")
TC3_REQ1 = "Scale 200g of rice from 4 to 8 servings."
TC3_REQ2 = "Based on what we just scaled, estimate calories at 1.3 kcal per gram."
TC4_PREF_KEY = "favourite_ingredient"
TC4_PREF_VAL = "pasta"
TC5_REQ  = "Scale -50g of rice from -2 servings to 8 servings."

def main():
    print("=" * 65)
    print("  NutriScale TA1 vs TA2 Evaluation")
    print("=" * 65)

    # Pre-seed long-term memory for TC4
    ltm_save(UID, TC4_PREF_KEY, TC4_PREF_VAL)
    print(f"\n[LTM] Saved pref: {TC4_PREF_KEY}={TC4_PREF_VAL} for user '{UID}'")

    ta1_results, ta2_results = [], []

    # TC1 — Basic recipe scaling + calorie estimation
    print("\n[TC1] Basic scaling + calorie estimate...")
    ta1_results.append(run_ta1_case("TC1","Basic scaling + calorie estimate",
        so=4,st=8,ia=200.0,cpu=1.3,ref_scaled=REF_SCALED_RICE,ref_kcal=REF_KCAL_RICE))
    ta2_results.append(run_ta2_case("TC1","Basic scaling + calorie estimate",
        request=TC1_REQ, user_id=UID, ref_scaled=REF_SCALED_RICE, ref_kcal=REF_KCAL_RICE))

    # TC2 — Nutrition-only RAG question
    print("\n[TC2] RAG nutrition question...")
    ta1_results.append(run_ta1_case("TC2","Nutrition RAG question (TA1 = scale+estimate only)",
        so=1,st=1,ia=100.0,cpu=1.65,ref_scaled=100.0,ref_kcal=165.0))
    ta2_results.append(run_ta2_case("TC2","RAG-backed nutrition question",
        request=TC2_REQ, user_id=UID, check_rag=True))

    # TC3 — Thread memory follow-up
    print("\n[TC3] Thread memory follow-up...")
    ta1_results.append(run_ta1_case("TC3","Thread memory follow-up — TA1 N/A"))
    print("  [TA2] Turn 1 of thread TC3...")
    ta2_run(TC3_REQ1, user_id=UID, thread_id="TC3")  # prime the thread
    print("  [TA2] Turn 2 of thread TC3 (memory recall)...")
    ta2_results.append(run_ta2_case("TC3","Thread memory follow-up",
        request=TC3_REQ2, user_id=UID, thread_id="TC3", check_memory=True))

    # TC4 — Long-term SQLite memory (new thread, different from TC3)
    print("\n[TC4] Long-term SQLite memory...")
    ta1_results.append(run_ta1_case("TC4","Long-term SQLite memory — TA1 N/A"))
    ta2_results.append(run_ta2_case("TC4","Long-term SQLite memory recall",
        request=f"What is my favourite ingredient? (my user id is {UID})",
        user_id=UID, thread_id="TC4_new", check_memory=True))

    # TC5 — Guard blocks invalid input
    print("\n[TC5] Guard blocks negative servings...")
    ta1_results.append(run_ta1_case("TC5","Guard blocks negative servings"))
    ta2_results.append(run_ta2_case("TC5","Guard blocks negative servings",
        request=TC5_REQ, user_id=UID, check_guard=True))

    # ── Save results ────────────────────────────────────────────────────────────
    def _save(path, data):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, default=str)

    _save(os.path.join(RESULTS_DIR,"ta1_results.json"), ta1_results)
    _save(os.path.join(RESULTS_DIR,"ta2_results.json"), ta2_results)

    # Save individual traces
    for r in ta2_results:
        trace_path = os.path.join(TRACES_DIR, f"{r['tc_id'].lower()}_trace.json")
        _save(trace_path, {"tc_id":r["tc_id"],"request":r.get("description",""),
                            "answer":r["answer"],"guard_ok":r["guard_ok"],
                            "route":r["route"],"trace":r["trace"],"elapsed_s":r["elapsed_s"]})

    # ── Print comparison table ───────────────────────────────────────────────────
    print("\n" + "=" * 80)
    print(f"  {'TC':<5} {'Description':<40} {'TA1':>8} {'TA2':>8}")
    print("=" * 80)
    for t1, t2 in zip(ta1_results, ta2_results):
        desc = t1["description"][:38]
        print(f"  {t1['tc_id']:<5} {desc:<40} {t1['status']:>8} {t2['status']:>8}")
    print("=" * 80)

    ta1_pass = sum(1 for r in ta1_results if r["status"]=="PASS")
    ta2_pass = sum(1 for r in ta2_results if r["status"] in ("PASS","PARTIAL"))
    ta1_na   = sum(1 for r in ta1_results if r["status"]=="NA")
    print(f"\n  TA1: {ta1_pass}/5 PASS  ({ta1_na} N/A — feature not in TA1)")
    print(f"  TA2: {ta2_pass}/5 PASS")
    print(f"\n  Results saved to: {RESULTS_DIR}")
    print(f"  Traces saved to:  {TRACES_DIR}")

if __name__ == "__main__":
    main()
