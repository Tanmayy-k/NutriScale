package com.nutriscale.app.ui.components

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Eco
import androidx.compose.material.icons.filled.Person
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.nutriscale.app.ui.theme.ForestGreen
import com.nutriscale.app.ui.theme.PureWhite
import com.nutriscale.app.ui.theme.SoftMint
import com.nutriscale.app.ui.theme.TextPrimary
import com.nutriscale.app.ui.theme.TextSecondary
import java.util.Calendar

@Composable
fun NutriScaleHeader(
    userName: String = "Tanmay",
    onProfileClick: () -> Unit = {}
) {
    val greeting = when (Calendar.getInstance().get(Calendar.HOUR_OF_DAY)) {
        in 5..11 -> "Good morning"
        in 12..16 -> "Good afternoon"
        in 17..21 -> "Good evening"
        else -> "Welcome back"
    }

    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = 20.dp, vertical = 16.dp),
        verticalAlignment = Alignment.CenterVertically
    ) {
        // Logo & Greeting
        Box(
            modifier = Modifier
                .size(44.dp)
                .clip(RoundedCornerShape(12.dp))
                .background(SoftMint),
            contentAlignment = Alignment.Center
        ) {
            Icon(
                imageVector = Icons.Default.Eco,
                contentDescription = "NutriScale Logo",
                tint = ForestGreen,
                modifier = Modifier.size(26.dp)
            )
        }

        Spacer(modifier = Modifier.width(12.dp))

        Row(
            modifier = Modifier.weight(1f),
            verticalAlignment = Alignment.CenterVertically
        ) {
            androidx.compose.foundation.layout.Column {
                Text(
                    text = "NutriScale",
                    style = MaterialTheme.typography.titleMedium.copy(
                        fontWeight = FontWeight.Bold,
                        color = ForestGreen,
                        letterSpacing = 0.5.sp
                    )
                )
                Text(
                    text = "$greeting, $userName",
                    style = MaterialTheme.typography.bodyMedium.copy(
                        color = TextSecondary
                    )
                )
            }
        }

        // Profile Avatar Button
        Surface(
            modifier = Modifier
                .size(42.dp)
                .clip(CircleShape),
            color = SoftMint,
            shadowElevation = 1.dp
        ) {
            IconButton(onClick = onProfileClick) {
                Icon(
                    imageVector = Icons.Default.Person,
                    contentDescription = "User Profile",
                    tint = ForestGreen,
                    modifier = Modifier.size(24.dp)
                )
            }
        }
    }
}
