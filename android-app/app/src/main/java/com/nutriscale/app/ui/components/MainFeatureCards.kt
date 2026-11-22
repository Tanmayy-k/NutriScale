package com.nutriscale.app.ui.components

import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowForwardIos
import androidx.compose.material.icons.filled.AutoAwesome
import androidx.compose.material.icons.filled.Scale
import androidx.compose.material.icons.filled.Security
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.nutriscale.app.ui.theme.ForestGreen
import com.nutriscale.app.ui.theme.PureWhite
import com.nutriscale.app.ui.theme.SoftMint
import com.nutriscale.app.ui.theme.TextPrimary
import com.nutriscale.app.ui.theme.TextSecondary

@Composable
fun MainFeatureCards(
    onNavigateToScaler: () -> Unit,
    onNavigateToAssistant: () -> Unit,
    onNavigateToAllergies: () -> Unit
) {
    Column(
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = 20.dp)
    ) {
        Text(
            text = "Agentic AI Features",
            style = MaterialTheme.typography.titleMedium.copy(
                fontWeight = FontWeight.Bold,
                color = TextPrimary
            )
        )

        Spacer(modifier = Modifier.height(12.dp))

        FeatureCardItem(
            title = "Recipe Scaler",
            description = "Deterministically scale ingredient weights and analyze exact calorie density with RAG grounding.",
            icon = Icons.Default.Scale,
            accentColor = ForestGreen,
            onClick = onNavigateToScaler
        )

        Spacer(modifier = Modifier.height(12.dp))

        FeatureCardItem(
            title = "Nutrition Assistant",
            description = "Natural-language multi-agent advisor for culinary guidance, macros, and nutrition exploration.",
            icon = Icons.Default.AutoAwesome,
            accentColor = Color(0xFF2E7D46),
            onClick = onNavigateToAssistant
        )

        Spacer(modifier = Modifier.height(12.dp))

        FeatureCardItem(
            title = "My Allergies & Guards",
            description = "Inspect stored user allergies, set dietary preferences, and audit pre-execution safety gating.",
            icon = Icons.Default.Security,
            accentColor = Color(0xFFC2410C),
            onClick = onNavigateToAllergies
        )
    }
}

@Composable
private fun FeatureCardItem(
    title: String,
    description: String,
    icon: ImageVector,
    accentColor: Color,
    onClick: () -> Unit
) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .clickable { onClick() },
        shape = RoundedCornerShape(16.dp),
        colors = CardDefaults.cardColors(containerColor = PureWhite),
        elevation = CardDefaults.cardElevation(defaultElevation = 1.5.dp)
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Surface(
                shape = RoundedCornerShape(12.dp),
                color = SoftMint,
                modifier = Modifier.size(48.dp)
            ) {
                Box(contentAlignment = Alignment.Center) {
                    Icon(
                        imageVector = icon,
                        contentDescription = title,
                        tint = accentColor,
                        modifier = Modifier.size(26.dp)
                    )
                }
            }

            Spacer(modifier = Modifier.width(16.dp))

            Column(modifier = Modifier.weight(1f)) {
                Text(
                    text = title,
                    style = MaterialTheme.typography.titleMedium.copy(
                        fontWeight = FontWeight.Bold,
                        color = TextPrimary
                    )
                )
                Spacer(modifier = Modifier.height(4.dp))
                Text(
                    text = description,
                    style = MaterialTheme.typography.bodySmall.copy(
                        color = TextSecondary,
                        lineHeight = 16.sp
                    )
                )
            }

            Spacer(modifier = Modifier.width(8.dp))

            Icon(
                imageVector = Icons.AutoMirrored.Filled.ArrowForwardIos,
                contentDescription = "Open",
                tint = TextSecondary.copy(alpha = 0.5f),
                modifier = Modifier.size(16.dp)
            )
        }
    }
}
