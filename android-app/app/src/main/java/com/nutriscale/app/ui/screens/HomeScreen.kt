package com.nutriscale.app.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.CloudDone
import androidx.compose.material.icons.filled.CloudOff
import androidx.compose.material.icons.filled.Refresh
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.unit.dp
import com.nutriscale.app.navigation.Screen
import com.nutriscale.app.ui.components.DailyNutritionOverviewCard
import com.nutriscale.app.ui.components.MainFeatureCards
import com.nutriscale.app.ui.components.NutriScaleHeader
import com.nutriscale.app.ui.components.RecentActivitySection
import com.nutriscale.app.ui.theme.ForestGreen
import com.nutriscale.app.ui.theme.OffWhite
import com.nutriscale.app.ui.theme.PureWhite
import com.nutriscale.app.ui.theme.SoftMint
import com.nutriscale.app.ui.theme.StatusAlertRed
import com.nutriscale.app.ui.theme.StatusAlertRedContainer
import com.nutriscale.app.ui.theme.StatusSuccessContainer
import com.nutriscale.app.ui.theme.StatusSuccessGreen
import com.nutriscale.app.ui.theme.TextPrimary
import com.nutriscale.app.ui.theme.TextSecondary
import com.nutriscale.app.viewmodel.NutriScaleViewModel

@Composable
fun HomeScreen(
    viewModel: NutriScaleViewModel,
    onNavigate: (Screen) -> Unit
) {
    val uiState by viewModel.uiState.collectAsState()
    val scrollState = rememberScrollState()

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(OffWhite)
            .verticalScroll(scrollState)
    ) {
        // Top Header
        NutriScaleHeader(
            userName = uiState.userId,
            onProfileClick = { onNavigate(Screen.AllergiesPreferences) }
        )

        // Backend Connection Pill & Status
        BackendStatusBar(
            isConnected = uiState.isConnected,
            statusText = uiState.connectionStatusMessage,
            modelName = uiState.modelName,
            isLoading = uiState.isLoading,
            onRetry = { viewModel.checkBackendHealth() }
        )

        Spacer(modifier = Modifier.height(16.dp))

        // Daily Nutrition Card
        DailyNutritionOverviewCard(
            consumedCalories = uiState.consumedCalories,
            targetCalories = uiState.targetCalories,
            proteinGrams = uiState.proteinGrams,
            targetProtein = uiState.targetProteinGrams,
            carbsGrams = uiState.carbsGrams,
            targetCarbs = uiState.targetCarbsGrams,
            fatGrams = uiState.fatGrams,
            targetFat = uiState.targetFatGrams
        )

        Spacer(modifier = Modifier.height(24.dp))

        // Three Main Feature Cards
        MainFeatureCards(
            onNavigateToScaler = { onNavigate(Screen.RecipeScaler) },
            onNavigateToAssistant = { onNavigate(Screen.NutritionAssistant) },
            onNavigateToAllergies = { onNavigate(Screen.AllergiesPreferences) }
        )

        Spacer(modifier = Modifier.height(24.dp))

        // Recent Scaling Activity
        RecentActivitySection(
            recentActivities = uiState.recentActivity
        )

        Spacer(modifier = Modifier.height(32.dp))
    }
}

@Composable
private fun BackendStatusBar(
    isConnected: Boolean?,
    statusText: String,
    modelName: String?,
    isLoading: Boolean,
    onRetry: () -> Unit
) {
    val bgColor = when (isConnected) {
        true -> StatusSuccessContainer
        false -> StatusAlertRedContainer
        null -> SoftMint
    }

    val contentColor = when (isConnected) {
        true -> StatusSuccessGreen
        false -> StatusAlertRed
        null -> ForestGreen
    }

    Card(
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = 20.dp),
        shape = RoundedCornerShape(12.dp),
        colors = CardDefaults.cardColors(containerColor = bgColor)
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(horizontal = 14.dp, vertical = 10.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Icon(
                imageVector = if (isConnected == true) Icons.Default.CloudDone else Icons.Default.CloudOff,
                contentDescription = "Backend Status",
                tint = contentColor,
                modifier = Modifier.size(20.dp)
            )

            Spacer(modifier = Modifier.width(10.dp))

            Column(modifier = Modifier.weight(1f)) {
                Text(
                    text = if (isConnected == true) "Ollama & Agents Connected" else "Backend Server",
                    style = MaterialTheme.typography.labelLarge.copy(color = contentColor)
                )
                Text(
                    text = statusText + if (modelName != null) " · Model: $modelName" else "",
                    style = MaterialTheme.typography.bodySmall.copy(color = TextSecondary),
                    maxLines = 1
                )
            }

            if (isLoading) {
                CircularProgressIndicator(
                    modifier = Modifier.size(18.dp),
                    strokeWidth = 2.dp,
                    color = contentColor
                )
            } else {
                IconButton(onClick = onRetry, modifier = Modifier.size(28.dp)) {
                    Icon(
                        imageVector = Icons.Default.Refresh,
                        contentDescription = "Retry Connection",
                        tint = contentColor,
                        modifier = Modifier.size(18.dp)
                    )
                }
            }
        }
    }
}
