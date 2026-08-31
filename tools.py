"""
tools.py — NutriScale
=====================
Defines the two @tool functions that the LangChain agent autonomously selects
and chains:

  1. scale_recipe      — scales an ingredient amount to a new serving count
  2. estimate_calories — multiplies a (scaled) ingredient amount by a per-unit
                         calorie value to produce a kcal estimate

Both tools include thorough input validation so the agent can surface
meaningful errors rather than silently producing wrong arithmetic.
"""

from langchain_core.tools import tool


# ─────────────────────────────────────────────────────────────────────────────
# Tool 1 – Recipe Scaler
# ─────────────────────────────────────────────────────────────────────────────

@tool
def scale_recipe(
    servings_original: float,
    servings_target: float,
    ingredient_amount: float,
) -> str:
    """
    Scale an ingredient amount from its original serving count to a target
    serving count.

    Use this tool FIRST whenever the user wants to scale a recipe.
    The result is the new (scaled) ingredient amount which should then be
    passed to estimate_calories.

    Args:
        servings_original: The number of servings the recipe currently makes.
                           Must be a positive number (> 0).
        servings_target:   The number of servings you want to make.
                           Must be a positive number (> 0).
        ingredient_amount: The amount of the ingredient for the original
                           serving count. Must be >= 0.

    Returns:
        A string describing the scaled ingredient amount, e.g.
        "Scaled ingredient amount: 400.0 units"
        Or an error message if any input is invalid.
    """
    # ── Validation ────────────────────────────────────────────────────────────
    try:
        servings_original = float(servings_original)
        servings_target   = float(servings_target)
        ingredient_amount = float(ingredient_amount)
    except (TypeError, ValueError):
        return "ERROR: All inputs must be valid numbers."

    if servings_original <= 0:
        return (
            f"ERROR: servings_original must be greater than 0 "
            f"(received {servings_original}). "
            "Cannot scale a recipe with zero or negative servings — "
            "that would cause division by zero or meaningless results."
        )

    if servings_target <= 0:
        return (
            f"ERROR: servings_target must be greater than 0 "
            f"(received {servings_target}). "
            "A recipe cannot be scaled to zero or negative servings."
        )

    if ingredient_amount < 0:
        return (
            f"ERROR: ingredient_amount cannot be negative "
            f"(received {ingredient_amount}). "
            "Physical quantities of ingredients cannot be less than zero."
        )

    # ── Calculation ───────────────────────────────────────────────────────────
    scaling_factor   = servings_target / servings_original
    scaled_amount    = ingredient_amount * scaling_factor

    return (
        f"Scaled ingredient amount: {scaled_amount:.2f} units "
        f"(original: {ingredient_amount} units for {servings_original} servings → "
        f"{scaled_amount:.2f} units for {servings_target} servings, "
        f"scaling factor: {scaling_factor:.4f})"
    )


# ─────────────────────────────────────────────────────────────────────────────
# Tool 2 – Calorie Estimator
# ─────────────────────────────────────────────────────────────────────────────

@tool
def estimate_calories(
    ingredient_amount: float,
    calories_per_unit: float,
) -> str:
    """
    Estimate the total calories for a given ingredient amount.

    Use this tool AFTER scale_recipe to calculate the calories for the
    scaled amount. Pass the scaled amount from scale_recipe as ingredient_amount.

    Args:
        ingredient_amount: The amount of the ingredient (e.g. grams, ml, pieces).
                           This should be the SCALED amount returned by scale_recipe.
                           Must be >= 0.
        calories_per_unit: Calories contained in one unit of the ingredient.
                           For example, rice has ~1.3 kcal per gram.
                           Must be >= 0.

    Returns:
        A string describing the estimated total calories, e.g.
        "Estimated calories: 520.0 kcal"
        Or an error message if any input is invalid.
    """
    # ── Validation ────────────────────────────────────────────────────────────
    try:
        ingredient_amount  = float(ingredient_amount)
        calories_per_unit  = float(calories_per_unit)
    except (TypeError, ValueError):
        return "ERROR: All inputs must be valid numbers."

    if ingredient_amount < 0:
        return (
            f"ERROR: ingredient_amount cannot be negative "
            f"(received {ingredient_amount}). "
            "Physical ingredient amounts must be zero or greater."
        )

    if calories_per_unit < 0:
        return (
            f"ERROR: calories_per_unit cannot be negative "
            f"(received {calories_per_unit}). "
            "Calorie density values must be zero or greater."
        )

    # ── Calculation ───────────────────────────────────────────────────────────
    total_calories = ingredient_amount * calories_per_unit

    return (
        f"Estimated calories: {total_calories:.2f} kcal "
        f"({ingredient_amount:.2f} units × {calories_per_unit} kcal/unit = "
        f"{total_calories:.2f} kcal)"
    )
