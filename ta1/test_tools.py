# -*- coding: utf-8 -*-
"""
test_tools.py -- NutriScale Unit Tests
=======================================
Tests both @tool functions against all required validation cases.
"""

import sys
import os
import re

# Allow running from the project root
sys.path.insert(0, os.path.dirname(__file__))

from tools import scale_recipe, estimate_calories


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

SEP = "-" * 65


def run_test(name: str, result: str, expect_error: bool = False) -> bool:
    """Print a formatted test result and return True if the test passed."""
    is_error = result.startswith("ERROR")
    passed   = (is_error == expect_error)
    status   = "PASS" if passed else "FAIL"
    tag      = "[ERROR]" if is_error else "[OK]   "
    print(f"  [{status}]  {name}")
    print(f"          {tag} {result}")
    print()
    return passed


# ---------------------------------------------------------------------------
# Test suite
# ---------------------------------------------------------------------------

def test_all() -> bool:
    results = []

    print("=" * 65)
    print("  NutriScale -- Tool Unit Tests")
    print("=" * 65)
    print()

    # -- scale_recipe: valid cases -------------------------------------------
    print("-- scale_recipe: valid cases --")

    r = scale_recipe.invoke({"servings_original": 4, "servings_target": 8, "ingredient_amount": 200.0})
    results.append(run_test("TC-01  Normal scale (4->8, 200g)", r, expect_error=False))

    r = scale_recipe.invoke({"servings_original": 4, "servings_target": 2, "ingredient_amount": 200.0})
    results.append(run_test("TC-02  Scale down (4->2, 200g -> 100g)", r, expect_error=False))

    r = scale_recipe.invoke({"servings_original": 1, "servings_target": 1, "ingredient_amount": 100.0})
    results.append(run_test("TC-03  Same servings (no change)", r, expect_error=False))

    r = scale_recipe.invoke({"servings_original": 4, "servings_target": 8, "ingredient_amount": 0.0})
    results.append(run_test("TC-04  Zero ingredient amount (valid)", r, expect_error=False))

    # -- scale_recipe: error cases -------------------------------------------
    print("-- scale_recipe: error cases --")

    r = scale_recipe.invoke({"servings_original": 0, "servings_target": 8, "ingredient_amount": 200.0})
    results.append(run_test("TC-05  servings_original = 0  --> ERROR", r, expect_error=True))

    r = scale_recipe.invoke({"servings_original": -2, "servings_target": 8, "ingredient_amount": 200.0})
    results.append(run_test("TC-06  servings_original < 0  --> ERROR", r, expect_error=True))

    r = scale_recipe.invoke({"servings_original": 4, "servings_target": 0, "ingredient_amount": 200.0})
    results.append(run_test("TC-07  servings_target = 0    --> ERROR", r, expect_error=True))

    r = scale_recipe.invoke({"servings_original": 4, "servings_target": -3, "ingredient_amount": 200.0})
    results.append(run_test("TC-08  servings_target < 0    --> ERROR", r, expect_error=True))

    r = scale_recipe.invoke({"servings_original": 4, "servings_target": 8, "ingredient_amount": -50.0})
    results.append(run_test("TC-09  ingredient_amount < 0  --> ERROR", r, expect_error=True))

    # -- estimate_calories: valid cases --------------------------------------
    print("-- estimate_calories: valid cases --")

    r = estimate_calories.invoke({"ingredient_amount": 400.0, "calories_per_unit": 1.3})
    results.append(run_test("TC-10  Normal estimate (400g x 1.3 -> 520 kcal)", r, expect_error=False))

    r = estimate_calories.invoke({"ingredient_amount": 0.0, "calories_per_unit": 1.3})
    results.append(run_test("TC-11  Zero amount (valid -> 0 kcal)", r, expect_error=False))

    r = estimate_calories.invoke({"ingredient_amount": 400.0, "calories_per_unit": 0.0})
    results.append(run_test("TC-12  Zero kcal/unit (valid -> 0 kcal)", r, expect_error=False))

    # -- estimate_calories: error cases --------------------------------------
    print("-- estimate_calories: error cases --")

    r = estimate_calories.invoke({"ingredient_amount": -100.0, "calories_per_unit": 1.3})
    results.append(run_test("TC-13  ingredient_amount < 0  --> ERROR", r, expect_error=True))

    r = estimate_calories.invoke({"ingredient_amount": 400.0, "calories_per_unit": -1.3})
    results.append(run_test("TC-14  calories_per_unit < 0  --> ERROR", r, expect_error=True))

    # -- Simulated autonomous chain: scale -> estimate -----------------------
    print("-- Simulated chain: scale_recipe -> estimate_calories --")

    scaled = scale_recipe.invoke({"servings_original": 4, "servings_target": 8, "ingredient_amount": 200.0})
    print(f"  scale_recipe result: {scaled}")

    try:
        match = re.search(r"Scaled ingredient amount: ([0-9.]+)", scaled)
        if match:
            scaled_amount    = float(match.group(1))
            calories_result  = estimate_calories.invoke(
                {"ingredient_amount": scaled_amount, "calories_per_unit": 1.3}
            )
            results.append(
                run_test("TC-15  Chain: scale(4->8, 200g) -> estimate(x1.3)", calories_result, expect_error=False)
            )
        else:
            print("  [FAIL]  TC-15  Could not parse scaled amount from result\n")
            results.append(False)
    except Exception as exc:
        print(f"  [FAIL]  TC-15  Exception: {exc}\n")
        results.append(False)

    # -- Summary -------------------------------------------------------------
    print("=" * 65)
    passed = sum(results)
    total  = len(results)
    print(f"  Results: {passed}/{total} tests passed")
    if passed == total:
        print("  All tests passed!")
    else:
        print(f"  WARNING: {total - passed} test(s) failed.")
    print("=" * 65)

    return passed == total


if __name__ == "__main__":
    success = test_all()
    sys.exit(0 if success else 1)
