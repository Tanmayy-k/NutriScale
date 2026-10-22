# -*- coding: utf-8 -*-
"""
allergen_tests.py — Dedicated test suite for allergen and ambiguous ingredient guards.
"""
import os, sys, json

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TA2 = os.path.join(ROOT, "ta2")
sys.path.insert(0, TA2)
from prototype import run as ta2_run, ltm_save_allergy, ltm_load_allergies

UID = "allergy_test_user"

def main():
    print("=" * 70)
    print("  NutriScale — Allergen & Ambiguity Guard Tests")
    print("=" * 70)

    # 1. Seed DB
    ltm_save_allergy(UID, "wheat")
    ltm_save_allergy(UID, "peanut")
    allergies = ltm_load_allergies(UID)
    print(f"[Seed] User '{UID}' allergies in DB: {allergies}\n")

    cases = [
        {
            "id": "ATC1",
            "name": "Matching declared allergy (direct)",
            "request": "Scale 200g of wheat bread from 4 to 8 servings and estimate calories",
            "thread_id": "atc1",
            "expected_guard_ok": False,
            "validate": lambda r: r.get("guard_ok") is False and "wheat" in (r.get("guard_reason") or ""),
        },
        {
            "id": "ATC2",
            "name": "No known match (safe ingredient)",
            "request": "Scale 200g of rice from 4 to 8 servings and estimate calories",
            "thread_id": "atc2",
            "expected_guard_ok": True,
            "validate": lambda r: r.get("guard_ok") is True,
        },
        {
            "id": "ATC3",
            "name": "Unknown/ambiguous ingredient",
            "request": "Scale 100g of unknown mystery ingredient from 2 to 4 servings",
            "thread_id": "atc3",
            "expected_guard_ok": False,
            "validate": lambda r: r.get("guard_ok") is False and "UNKNOWN" in (r.get("guard_reason") or ""),
        },
        {
            "id": "ATC4",
            "name": "Alias/Synonym match (peanut -> groundnut)",
            "request": "Scale 50g of groundnut sauce from 2 to 4 servings",
            "thread_id": "atc4",
            "expected_guard_ok": False,
            "validate": lambda r: r.get("guard_ok") is False and "peanut" in (r.get("guard_reason") or "") and "groundnut" in (r.get("guard_reason") or ""),
        },
    ]

    traces = []
    all_passed = True

    for c in cases:
        print(f"Running {c['id']}: {c['name']}...")
        res = ta2_run(c["request"], user_id=UID, thread_id=c["thread_id"])
        passed = c["validate"](res)
        status = "PASS" if passed else "FAIL"
        if not passed:
            all_passed = False

        print(f"  Request:      {c['request']}")
        print(f"  Guard OK:     {res.get('guard_ok')}")
        print(f"  Guard Reason: {res.get('guard_reason')}")
        print(f"  Answer:       {res.get('answer', '')[:100]}...")
        print(f"  Result:       [{status}]\n")

        trace_entry = {
            "case_id": c["id"],
            "name": c["name"],
            "request": c["request"],
            "user_id": UID,
            "thread_id": c["thread_id"],
            "guard_ok": res.get("guard_ok"),
            "guard_reason": res.get("guard_reason"),
            "answer": res.get("answer"),
            "route": res.get("route"),
            "trace": res.get("trace"),
            "status": status,
        }
        traces.append(trace_entry)

    # Save results
    out_dir = os.path.join(TA2, "results", "traces")
    os.makedirs(out_dir, exist_ok=True)
    trace_path = os.path.join(out_dir, "allergen_tests_trace.json")
    with open(trace_path, "w", encoding="utf-8") as f:
        json.dump(traces, f, indent=2)

    print("=" * 70)
    print("Summary:")
    for t in traces:
        print(f"  {t['case_id']}: {t['name']:<30} [{t['status']}]")
    print(f"\nTrace saved to: {trace_path}")
    print("=" * 70)

    if not all_passed:
        sys.exit(1)

if __name__ == "__main__":
    main()
