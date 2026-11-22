package com.nutriscale.app.ui.theme

import android.app.Activity
import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.runtime.SideEffect
import androidx.compose.ui.graphics.toArgb
import androidx.compose.ui.platform.LocalView
import androidx.core.view.WindowCompat

private val LightColorScheme = lightColorScheme(
    primary = ForestGreen,
    onPrimary = PureWhite,
    primaryContainer = SoftMint,
    onPrimaryContainer = DarkForestGreen,
    secondary = LightForestGreen,
    onSecondary = PureWhite,
    secondaryContainer = MintGreenCard,
    onSecondaryContainer = DarkForestGreen,
    tertiary = MintAccent,
    background = OffWhite,
    onBackground = TextPrimary,
    surface = PureWhite,
    onSurface = TextPrimary,
    surfaceVariant = SurfaceVariant,
    onSurfaceVariant = TextSecondary,
    outline = OutlineBorder
)

@Composable
fun NutriScaleTheme(
    darkTheme: Boolean = isSystemInDarkTheme(),
    content: @Composable () -> Unit
) {
    val colorScheme = LightColorScheme // Maintain clean premium off-white/forest green palette
    val view = LocalView.current
    if (!view.isInEditMode) {
        SideEffect {
            val window = (view.context as? Activity)?.window
            window?.let {
                it.statusBarColor = ForestGreen.toArgb()
                WindowCompat.getInsetsController(it, view).isAppearanceLightStatusBars = false
            }
        }
    }

    MaterialTheme(
        colorScheme = colorScheme,
        typography = Typography,
        content = content
    )
}
