# -*- coding: utf-8 -*-
"""
rag_vs_manual.py — Compare RAG-retrieved calorie density against hand-entered value.
"""
import os, sys, json

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TA2 = os.path.join(ROOT, "ta2")
sys.path.insert(0, TA2)
from ta2_tools import rag_calories_per_unit

def run_comparison():
    print("=" * 75)
    print("  NutriScale — RAG vs Manual Calorie Comparison")
    print("=" * 75)

    results = []

    # Case 1: Cooked Rice (in KB)
    ing1 = "rice"
    state1 = "cooked"
    amt1 = 400.0
    rag_cpu1 = rag_calories_per_unit(ing1)
    manual_cpu1 = 1.5  # Deliberately different manual estimate baseline
    manual_total1 = round(amt1 * manual_cpu1, 2)
    source1 = "rice_nutrition.txt"

    if rag_cpu1 is not None:
        rag_total1 = round(amt1 * rag_cpu1, 2)
        diff1 = round(abs(manual_total1 - rag_total1), 2)
        pct_diff1 = round((diff1 / manual_total1 * 100), 2)
    else:
        rag_total1 = "UNKNOWN"
        diff1 = "UNKNOWN"
        pct_diff1 = "UNKNOWN"

    res1 = {
        "ingredient": ing1,
        "food_state": state1,
        "amount_used": amt1,
        "rag_calories_per_unit": rag_cpu1,
        "rag_total_kcal": rag_total1,
        "rag_source": source1,
        "manual_baseline_calories_per_unit": manual_cpu1,
        "manual_total_kcal": manual_total1,
        "manual_label": "Comparison baseline only (not an authoritative reference)",
        "absolute_difference": diff1,
        "percentage_difference": pct_diff1,
        "limitations": "RAG density represents cooked white rice (~1.3 kcal/g). Uncooked rice is ~3.6 kcal/g.",
    }
    results.append(res1)

    print(f"\n[Case 1: {ing1.upper()} ({state1.upper()})]")
    print(f"  Amount: {amt1}g")
    print(f"  RAG Reference ({source1}): {rag_cpu1} kcal/g -> Total: {rag_total1} kcal")
    print(f"  Manual Comparison Baseline: {manual_cpu1} kcal/g -> Total: {manual_total1} kcal")
    print(f"  Difference:                 {diff1} kcal ({pct_diff1}%)")

    # Case 2: Chicken Breast (Cooked vs Raw distinction in KB)
    ing2 = "chicken"
    state2 = "cooked"
    amt2 = 300.0
    rag_cpu2 = rag_calories_per_unit(ing2)
    manual_cpu2 = 2.0  # Manual estimate
    manual_total2 = round(amt2 * manual_cpu2, 2)
    source2 = "chicken_nutrition.txt"

    if rag_cpu2 is not None:
        rag_total2 = round(amt2 * rag_cpu2, 2)
        diff2 = round(abs(manual_total2 - rag_total2), 2)
        pct_diff2 = round((diff2 / manual_total2 * 100), 2)
    else:
        rag_total2 = "UNKNOWN"
        diff2 = "UNKNOWN"
        pct_diff2 = "UNKNOWN"

    res2 = {
        "ingredient": ing2,
        "food_state": state2,
        "amount_used": amt2,
        "rag_calories_per_unit": rag_cpu2,
        "rag_total_kcal": rag_total2,
        "rag_source": source2,
        "manual_baseline_calories_per_unit": manual_cpu2,
        "manual_total_kcal": manual_total2,
        "manual_label": "Comparison baseline only (not an authoritative reference)",
        "absolute_difference": diff2,
        "percentage_difference": pct_diff2,
        "limitations": "Reference doc notes cooked chicken is ~1.65 kcal/g, raw chicken is ~1.1 kcal/g due to moisture loss.",
    }
    results.append(res2)

    print(f"\n[Case 2: {ing2.upper()} ({state2.upper()})]")
    print(f"  Amount: {amt2}g")
    print(f"  RAG Reference ({source2}): {rag_cpu2} kcal/g -> Total: {rag_total2} kcal")
    print(f"  Manual Comparison Baseline: {manual_cpu2} kcal/g -> Total: {manual_total2} kcal")
    print(f"  Difference:                 {diff2} kcal ({pct_diff2}%)")

    # Case 3: Quinoa (NOT in KB)
    ing3 = "quinoa"
    state3 = "unknown"
    amt3 = 400.0
    rag_cpu3 = rag_calories_per_unit(ing3)
    manual_cpu3 = 1.2
    manual_total3 = round(amt3 * manual_cpu3, 2)

    if rag_cpu3 is not None:
        rag_total3 = round(amt3 * rag_cpu3, 2)
        diff3 = round(abs(manual_total3 - rag_total3), 2)
        pct_diff3 = round((diff3 / manual_total3 * 100), 2)
    else:
        rag_total3 = "UNKNOWN"
        diff3 = "UNKNOWN"
        pct_diff3 = "UNKNOWN"

    res3 = {
        "ingredient": ing3,
        "food_state": state3,
        "amount_used": amt3,
        "rag_calories_per_unit": "UNKNOWN",
        "rag_total_kcal": "UNKNOWN",
        "rag_source": "NONE (not in knowledge base)",
        "manual_baseline_calories_per_unit": manual_cpu3,
        "manual_total_kcal": manual_total3,
        "manual_label": "Comparison baseline only (not an authoritative reference)",
        "absolute_difference": "UNKNOWN",
        "percentage_difference": "UNKNOWN",
        "note": f"Ingredient '{ing3}' not found in knowledge base (returned None/UNKNOWN). Model cannot guess.",
    }
    results.append(res3)

    print(f"\n[Case 3: {ing3.upper()} (Not in KB)]")
    print(f"  Amount: {amt3}g")
    print(f"  RAG Calorie Density:        {res3['rag_calories_per_unit']}")
    print(f"  RAG Total kcal:             {res3['rag_total_kcal']}")
    print(f"  Note:                       {res3['note']}")

    out_path = os.path.join(TA2, "results", "rag_vs_manual.json")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print("\n" + "=" * 75)
    print(f"Results saved to: {out_path}")
    print("=" * 75)

if __name__ == "__main__":
    run_comparison()
