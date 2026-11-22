package com.nutriscale.app.ui.components

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.LinearProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.nutriscale.app.ui.theme.ForestGreen
import com.nutriscale.app.ui.theme.MintAccent
import com.nutriscale.app.ui.theme.PureWhite
import com.nutriscale.app.ui.theme.SoftMint
import com.nutriscale.app.ui.theme.TextPrimary
import com.nutriscale.app.ui.theme.TextSecondary

@Composable
fun DailyNutritionOverviewCard(
    consumedCalories: Int,
    targetCalories: Int,
    proteinGrams: Int,
    targetProtein: Int,
    carbsGrams: Int,
    targetCarbs: Int,
    fatGrams: Int,
    targetFat: Int
) {
    val progress = (consumedCalories.toFloat() / targetCalories.toFloat()).coerceIn(0f, 1f)

    Card(
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = 20.dp),
        shape = RoundedCornerShape(20.dp),
        colors = CardDefaults.cardColors(containerColor = PureWhite),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
    ) {
        Column(
            modifier = Modifier.padding(20.dp)
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    text = "Daily Nutrition",
                    style = MaterialTheme.typography.titleMedium.copy(
                        fontWeight = FontWeight.Bold,
                        color = TextPrimary
                    )
                )
                Text(
                    text = "Goal: $targetCalories kcal",
                    style = MaterialTheme.typography.bodySmall.copy(
                        color = ForestGreen,
                        fontWeight = FontWeight.SemiBold
                    )
                )
            }

            Spacer(modifier = Modifier.height(14.dp))

            // Calorie progress bar
            Row(
                modifier = Modifier.fillMaxWidth(),
                verticalAlignment = Alignment.Bottom
            ) {
                Text(
                    text = "$consumedCalories",
                    style = MaterialTheme.typography.headlineLarge.copy(
                        fontWeight = FontWeight.Bold,
                        color = ForestGreen
                    )
                )
                Text(
                    text = " / $targetCalories kcal",
                    style = MaterialTheme.typography.bodyLarge.copy(
                        color = TextSecondary
                    ),
                    modifier = Modifier.padding(bottom = 4.dp, start = 4.dp)
                )
            }

            Spacer(modifier = Modifier.height(10.dp))

            LinearProgressIndicator(
                progress = { progress },
                modifier = Modifier
                    .fillMaxWidth()
                    .height(8.dp)
                    .clip(RoundedCornerShape(4.dp)),
                color = ForestGreen,
                trackColor = SoftMint
            )

            Spacer(modifier = Modifier.height(20.dp))

            // Macro summary split
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                MacroPill(
                    label = "Protein",
                    current = proteinGrams,
                    target = targetProtein,
                    color = Color(0xFF2E7D46)
                )
                MacroPill(
                    label = "Carbs",
                    current = carbsGrams,
                    target = targetCarbs,
                    color = Color(0xFFD97706)
                )
                MacroPill(
                    label = "Fats",
                    current = fatGrams,
                    target = targetFat,
                    color = Color(0xFF2563EB)
                )
            }
        }
    }
}

@Composable
private fun MacroPill(
    label: String,
    current: Int,
    target: Int,
    color: Color
) {
    Column(
        modifier = Modifier
            .clip(RoundedCornerShape(12.dp))
            .background(SoftMint.copy(alpha = 0.5f))
            .padding(horizontal = 14.dp, vertical = 10.dp),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Text(
            text = label,
            style = MaterialTheme.typography.bodySmall.copy(
                fontWeight = FontWeight.Medium,
                color = TextSecondary
            )
        )
        Spacer(modifier = Modifier.height(4.dp))
        Text(
            text = "${current}g",
            style = MaterialTheme.typography.titleMedium.copy(
                fontWeight = FontWeight.Bold,
                color = color
            )
        )
        Text(
            text = "of ${target}g",
            style = MaterialTheme.typography.bodySmall.copy(
                fontSize = 11.sp,
                color = TextSecondary
            )
        )
    }
}
