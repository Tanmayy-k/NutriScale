package com.nutriscale.app

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Scaffold
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.currentBackStackEntryAsState
import androidx.navigation.compose.rememberNavController
import com.nutriscale.app.navigation.Screen
import com.nutriscale.app.ui.components.NutriScaleBottomNav
import com.nutriscale.app.ui.screens.AllergiesPreferencesScreen
import com.nutriscale.app.ui.screens.HomeScreen
import com.nutriscale.app.ui.screens.NutritionAssistantScreen
import com.nutriscale.app.ui.screens.RecipeScalerScreen
import com.nutriscale.app.ui.theme.NutriScaleTheme
import com.nutriscale.app.viewmodel.NutriScaleViewModel

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            NutriScaleTheme {
                NutriScaleApp()
            }
        }
    }
}

@Composable
fun NutriScaleApp() {
    val navController = rememberNavController()
    val viewModel: NutriScaleViewModel = viewModel()
    val navBackStackEntry by navController.currentBackStackEntryAsState()
    val currentRoute = navBackStackEntry?.destination?.route ?: Screen.Home.route

    Scaffold(
        modifier = Modifier.fillMaxSize(),
        bottomBar = {
            NutriScaleBottomNav(
                currentRoute = currentRoute,
                onNavigate = { targetScreen ->
                    if (currentRoute != targetScreen.route) {
                        navController.navigate(targetScreen.route) {
                            popUpTo(Screen.Home.route) {
                                saveState = true
                            }
                            launchSingleTop = true
                            restoreState = true
                        }
                    }
                }
            )
        }
    ) { paddingValues ->
        NavHost(
            navController = navController,
            startDestination = Screen.Home.route,
            modifier = Modifier.padding(paddingValues)
        ) {
            composable(Screen.Home.route) {
                HomeScreen(
                    viewModel = viewModel,
                    onNavigate = { screen -> navController.navigate(screen.route) }
                )
            }
            composable(Screen.RecipeScaler.route) {
                RecipeScalerScreen(
                    viewModel = viewModel,
                    onBack = { navController.popBackStack() }
                )
            }
            composable(Screen.NutritionAssistant.route) {
                NutritionAssistantScreen(
                    viewModel = viewModel,
                    onBack = { navController.popBackStack() }
                )
            }
            composable(Screen.AllergiesPreferences.route) {
                AllergiesPreferencesScreen(
                    viewModel = viewModel,
                    onBack = { navController.popBackStack() }
                )
            }
        }
    }
}
