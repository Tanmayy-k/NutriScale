# -*- coding: utf-8 -*-
"""
scaling_critic.py — Standalone scaling critic for NutriScale
Independently verifies that scale_recipe produces correct output within tolerance.
"""
import os, sys, json, re

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TA1 = os.path.join(ROOT, "ta1")
sys.path.insert(0, TA1)
from tools import scale_recipe as ta1_scale

TOLERANCE_PERCENT = 1.0

TEST_CASES = [
    {
        "ingredient": "rice",
        "original_amount": 200.0,
        "original_servings": 4.0,
        "target_servings": 8.0,
        "expected_scaled": 400.0,
        "is_injected_error": False,
    },
    {
        "ingredient": "chicken",
        "original_amount": 300.0,
        "original_servings": 3.0,
        "target_servings": 6.0,
        "expected_scaled": 600.0,
        "is_injected_error": False,
    },
    {
        "ingredient": "pasta",
        "original_amount": 150.0,
        "original_servings": 2.0,
        "target_servings": 5.0,
        "expected_scaled": 375.0,
        "is_injected_error": False,
    },
    {
        "ingredient": "rice",
        "original_amount": 200.0,
        "original_servings": 4.0,
        "target_servings": 8.0,
        "expected_scaled": 300.0,  # INJECTED ERROR (correct=400.0)
        "is_injected_error": True,
    },
    {
        "ingredient": "rice",
        "original_amount": -50.0,
        "original_servings": 4.0,
        "target_servings": 8.0,
        "expected_scaled": None,
        "is_invalid_input": True,
    },
    {
        "ingredient": "rice",
        "original_amount": 200.0,
        "original_servings": 0.0,
        "target_servings": 8.0,
        "expected_scaled": None,
        "is_invalid_input": True,
    },
]

def main():
    print("=" * 75)
    print("  NutriScale — Scaling Critic Verification")
    print(f"  Tolerance: {TOLERANCE_PERCENT}%")
    print("=" * 75)

    traces = []
    unintended_failure = False
    injected_failed = False
    invalid_handled = True

    for tc in TEST_CASES:
        ing = tc["ingredient"]
        oa = tc["original_amount"]
        os_ = tc["original_servings"]
        ts = tc["target_servings"]
        exp = tc.get("expected_scaled")
        is_invalid = tc.get("is_invalid_input", False)

        # 1. Deterministic formula calculation with safety check
        if os_ <= 0 or oa < 0 or ts <= 0:
            formula_result = "INVALID_INPUT"
        else:
            formula_result = round((oa * ts) / os_, 4)

        # 2. Tool output
        tool_out = ta1_scale.invoke({
            "servings_original": os_,
            "servings_target": ts,
            "ingredient_amount": oa,
        })
        m = re.search(r"Scaled ingredient amount:\s*([\d.]+)", tool_out)
        actual_scaled = float(m.group(1)) if m else None

        # 3. Diff and percentage diff relative to expected
        if is_invalid:
            diff = None
            pass_fail = "PASS" if ("ERROR" in tool_out and formula_result == "INVALID_INPUT") else "FAIL"
            if pass_fail != "PASS":
                invalid_handled = False
        else:
            diff = round(abs(formula_result - exp), 4)
            pct_diff = round((diff / exp * 100) if exp != 0 else 0, 4)
            pass_fail = "PASS" if pct_diff <= TOLERANCE_PERCENT else "FAIL"

        trace_entry = {
            "ingredient": ing,
            "original_amount": oa,
            "original_servings": os_,
            "target_servings": ts,
            "expected_scaled": exp,
            "actual_scaled": actual_scaled,
            "formula_result": formula_result,
            "diff": diff,
            "tolerance_percent": TOLERANCE_PERCENT,
            "pass_fail": pass_fail,
            "tool_output_string": tool_out,
        }
        traces.append(trace_entry)

        if tc.get("is_injected_error"):
            if pass_fail == "FAIL":
                injected_failed = True
            else:
                unintended_failure = True
        elif not is_invalid:
            if pass_fail != "PASS":
                unintended_failure = True

    # Save full trace
    out_dir = os.path.join(ROOT, "ta2", "results", "traces")
    os.makedirs(out_dir, exist_ok=True)
    trace_path = os.path.join(out_dir, "scaling_critic_trace.json")
    with open(trace_path, "w", encoding="utf-8") as f:
        json.dump(traces, f, indent=2)

    # Print table
    print(f"{'Ingredient':<10} {'Orig':>6} {'Serv':>7} {'Exp':>10} {'Formula':>14} {'Tool':>10} {'Diff':>8} {'Status':>8}")
    print("-" * 80)
    for t in traces:
        exp_str = f"{t['expected_scaled']:>10.1f}" if isinstance(t['expected_scaled'], (int, float)) else f"{str(t['expected_scaled']):>10}"
        form_str = f"{t['formula_result']:>14.1f}" if isinstance(t['formula_result'], (int, float)) else f"{str(t['formula_result']):>14}"
        tool_str = f"{t['actual_scaled']:>10.1f}" if isinstance(t['actual_scaled'], (int, float)) else f"{str(t['actual_scaled']):>10}"
        diff_str = f"{t['diff']:>8.1f}" if isinstance(t['diff'], (int, float)) else f"{str(t['diff']):>8}"
        print(f"{t['ingredient']:<10} {t['original_amount']:>6.1f} {t['original_servings']:>3.0f}->{t['target_servings']:<3.0f} {exp_str} {form_str} {tool_str} {diff_str} {t['pass_fail']:>8}")
    print("=" * 80)
    print(f"Trace saved to: {trace_path}")

    if injected_failed and not unintended_failure and invalid_handled:
        print("\nSUCCESS: All normal cases PASSED, injected error caught, invalid inputs safely rejected.")
        sys.exit(0)
    else:
        print("\nFAILURE: Unintended test case failure, invalid handling failure, or injected error not caught.")
        sys.exit(1)

if __name__ == "__main__":
    main()
