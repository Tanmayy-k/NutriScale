package com.nutriscale.app.ui.components

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.History
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.nutriscale.app.data.models.ScaleResponse
import com.nutriscale.app.ui.theme.ForestGreen
import com.nutriscale.app.ui.theme.PureWhite
import com.nutriscale.app.ui.theme.SoftMint
import com.nutriscale.app.ui.theme.TextPrimary
import com.nutriscale.app.ui.theme.TextSecondary

@Composable
fun RecentActivitySection(
    recentActivities: List<ScaleResponse>
) {
    Column(
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = 20.dp)
    ) {
        Text(
            text = "Recent Scaling Activity",
            style = MaterialTheme.typography.titleMedium.copy(
                fontWeight = FontWeight.Bold,
                color = TextPrimary
            )
        )

        Spacer(modifier = Modifier.height(12.dp))

        if (recentActivities.isEmpty()) {
            // Clean honest empty state instead of fabricated mock history
            Card(
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(16.dp),
                colors = CardDefaults.cardColors(containerColor = PureWhite),
                elevation = CardDefaults.cardElevation(defaultElevation = 1.dp)
            ) {
                Column(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(24.dp),
                    horizontalAlignment = Alignment.CenterHorizontally
                ) {
                    Icon(
                        imageVector = Icons.Default.History,
                        contentDescription = "Empty History",
                        tint = TextSecondary.copy(alpha = 0.5f),
                        modifier = Modifier.padding(bottom = 8.dp)
                    )
                    Text(
                        text = "No Recent Activity",
                        style = MaterialTheme.typography.titleMedium.copy(
                            fontWeight = FontWeight.SemiBold,
                            color = TextPrimary
                        )
                    )
                    Spacer(modifier = Modifier.height(4.dp))
                    Text(
                        text = "When you scale a recipe or query the nutrition assistant, your session history will appear here.",
                        style = MaterialTheme.typography.bodySmall.copy(
                            color = TextSecondary
                        ),
                        textAlign = androidx.compose.ui.text.style.TextAlign.Center
                    )
                }
            }
        } else {
            Column(verticalArrangement = Arrangement.spacedBy(10.dp)) {
                recentActivities.forEach { item ->
                    Card(
                        modifier = Modifier.fillMaxWidth(),
                        shape = RoundedCornerShape(14.dp),
                        colors = CardDefaults.cardColors(containerColor = PureWhite),
                        elevation = CardDefaults.cardElevation(defaultElevation = 1.dp)
                    ) {
                        Row(
                            modifier = Modifier
                                .fillMaxWidth()
                                .padding(16.dp),
                            horizontalArrangement = Arrangement.SpaceBetween,
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Column {
                                Text(
                                    text = item.ingredient_name.replaceFirstChar { if (it.isLowerCase()) it.titlecase() else it.toString() },
                                    style = MaterialTheme.typography.titleMedium.copy(
                                        fontWeight = FontWeight.Bold,
                                        color = TextPrimary
                                    )
                                )
                                Text(
                                    text = "${item.original_amount}g (${item.original_servings.toInt()} serv) → ${item.scaled_amount}g (${item.target_servings.toInt()} serv)",
                                    style = MaterialTheme.typography.bodySmall.copy(
                                        color = TextSecondary
                                    )
                                )
                            }
                            Column(horizontalAlignment = Alignment.End) {
                                Text(
                                    text = item.estimated_calories?.let { "${it.toInt()} kcal" } ?: "UNKNOWN",
                                    style = MaterialTheme.typography.titleMedium.copy(
                                        fontWeight = FontWeight.Bold,
                                        color = ForestGreen
                                    )
                                )
                                Text(
                                    text = "${item.scale_factor}x factor",
                                    style = MaterialTheme.typography.bodySmall.copy(
                                        color = TextSecondary
                                    )
                                )
                            }
                        }
                    }
                }
            }
        }
    }
}
