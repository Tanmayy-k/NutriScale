package com.nutriscale.app.ui.components

import androidx.compose.foundation.layout.RowScope
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.AutoAwesome
import androidx.compose.material.icons.filled.Home
import androidx.compose.material.icons.filled.Person
import androidx.compose.material.icons.filled.Scale
import androidx.compose.material3.Icon
import androidx.compose.material3.NavigationBar
import androidx.compose.material3.NavigationBarItem
import androidx.compose.material3.NavigationBarItemDefaults
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.unit.dp
import com.nutriscale.app.navigation.Screen
import com.nutriscale.app.ui.theme.DarkForestGreen
import com.nutriscale.app.ui.theme.ForestGreen
import com.nutriscale.app.ui.theme.PureWhite
import com.nutriscale.app.ui.theme.SoftMint
import com.nutriscale.app.ui.theme.TextSecondary

data class NavItem(
    val screen: Screen,
    val icon: ImageVector,
    val label: String
)

@Composable
fun NutriScaleBottomNav(
    currentRoute: String,
    onNavigate: (Screen) -> Unit
) {
    val items = listOf(
        NavItem(Screen.Home, Icons.Default.Home, "Home"),
        NavItem(Screen.RecipeScaler, Icons.Default.Scale, "Recipes"),
        NavItem(Screen.NutritionAssistant, Icons.Default.AutoAwesome, "Assistant"),
        NavItem(Screen.AllergiesPreferences, Icons.Default.Person, "Profile")
    )

    NavigationBar(
        containerColor = PureWhite,
        tonalElevation = 6.dp
    ) {
        items.forEach { item ->
            val selected = currentRoute == item.screen.route
            NavigationBarItem(
                selected = selected,
                onClick = { onNavigate(item.screen) },
                icon = {
                    Icon(
                        imageVector = item.icon,
                        contentDescription = item.label
                    )
                },
                label = { Text(item.label) },
                colors = NavigationBarItemDefaults.colors(
                    selectedIconColor = ForestGreen,
                    selectedTextColor = ForestGreen,
                    indicatorColor = SoftMint,
                    unselectedIconColor = TextSecondary,
                    unselectedTextColor = TextSecondary
                )
            )
        }
    }
}
