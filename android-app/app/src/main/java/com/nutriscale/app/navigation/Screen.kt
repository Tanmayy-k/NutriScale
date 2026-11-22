package com.nutriscale.app.navigation

sealed class Screen(val route: String, val title: String) {
    object Home : Screen("home", "Home")
    object RecipeScaler : Screen("recipe_scaler", "Recipe Scaler")
    object NutritionAssistant : Screen("nutrition_assistant", "Assistant")
    object AllergiesPreferences : Screen("allergies_preferences", "Profile")
}
