package com.nutriscale.app.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.ExperimentalLayoutApi
import androidx.compose.foundation.layout.FlowRow
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.imePadding
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.Add
import androidx.compose.material.icons.filled.CheckCircle
import androidx.compose.material.icons.filled.Close
import androidx.compose.material.icons.filled.CloudDone
import androidx.compose.material.icons.filled.CloudOff
import androidx.compose.material.icons.filled.Person
import androidx.compose.material.icons.filled.Security
import androidx.compose.material.icons.filled.Settings
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.OutlinedTextFieldDefaults
import androidx.compose.material3.Scaffold
import androidx.compose.material3.SuggestionChip
import androidx.compose.material3.SuggestionChipDefaults
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.material3.TopAppBarDefaults
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.nutriscale.app.ui.theme.DarkForestGreen
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

@OptIn(ExperimentalMaterial3Api::class, ExperimentalLayoutApi::class)
@Composable
fun AllergiesPreferencesScreen(
    viewModel: NutriScaleViewModel,
    onBack: () -> Unit
) {
    val uiState by viewModel.uiState.collectAsState()
    var newAllergenText by remember { mutableStateOf("") }
    var backendUrlInput by remember { mutableStateOf(uiState.backendUrl) }

    val commonAllergens = listOf("peanut", "dairy", "wheat", "gluten", "egg", "soy", "tree nuts")
    val networkPresets = listOf(
        Pair("Laptop Wi-Fi", "http://10.195.245.213:8000/"),
        Pair("Emulator", "http://10.0.2.2:8000/"),
        Pair("Localhost", "http://127.0.0.1:8000/")
    )

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Profile & Settings", fontWeight = FontWeight.Bold) },
                navigationIcon = {
                    IconButton(onClick = onBack) {
                        Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = "Back", tint = PureWhite)
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = ForestGreen,
                    titleContentColor = PureWhite
                )
            )
        }
    ) { paddingValues ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .background(OffWhite)
                .padding(paddingValues)
                .imePadding()
                .verticalScroll(rememberScrollState())
                .padding(20.dp)
        ) {
            // User Profile Card
            Card(
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(16.dp),
                colors = CardDefaults.cardColors(containerColor = PureWhite),
                elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
            ) {
                Row(
                    modifier = Modifier.padding(16.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Box(
                        modifier = Modifier
                            .size(46.dp)
                            .clip(CircleShape)
                            .background(SoftMint),
                        contentAlignment = Alignment.Center
                    ) {
                        Icon(Icons.Default.Person, contentDescription = null, tint = ForestGreen, modifier = Modifier.size(26.dp))
                    }
                    Spacer(modifier = Modifier.width(14.dp))
                    Column {
                        Text(
                            text = "Active Profile",
                            style = MaterialTheme.typography.labelSmall.copy(color = TextSecondary)
                        )
                        Text(
                            text = uiState.userId,
                            style = MaterialTheme.typography.titleMedium.copy(
                                fontWeight = FontWeight.Bold,
                                color = TextPrimary
                            )
                        )
                        Text(
                            text = "Persistent memory active in SQLite (ta2/memory.db)",
                            style = MaterialTheme.typography.bodySmall.copy(color = ForestGreen)
                        )
                    }
                }
            }

            Spacer(modifier = Modifier.height(20.dp))

            // Declared Allergens Card (Pre-Execution Guard)
            Card(
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(16.dp),
                colors = CardDefaults.cardColors(containerColor = PureWhite),
                elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
            ) {
                Column(modifier = Modifier.padding(18.dp)) {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            Icon(Icons.Default.Security, contentDescription = null, tint = StatusAlertRed)
                            Text(
                                text = "Declared Allergens Guard",
                                style = MaterialTheme.typography.titleMedium.copy(
                                    fontWeight = FontWeight.Bold,
                                    color = TextPrimary
                                ),
                                modifier = Modifier.padding(start = 8.dp)
                            )
                        }
                        Box(
                            modifier = Modifier
                                .clip(RoundedCornerShape(6.dp))
                                .background(StatusAlertRedContainer)
                                .padding(horizontal = 6.dp, vertical = 2.dp)
                        ) {
                            Text(
                                text = "${uiState.allergies.size} Active",
                                color = StatusAlertRed,
                                style = MaterialTheme.typography.labelSmall.copy(fontWeight = FontWeight.Bold)
                            )
                        }
                    }

                    Text(
                        text = "Any recipe scaling or meal recommendation containing these allergens (or their aliases like milk ↔ dairy) is blocked by the Allergen Guard before running.",
                        style = MaterialTheme.typography.bodySmall.copy(color = TextSecondary),
                        modifier = Modifier.padding(top = 6.dp, bottom = 14.dp)
                    )

                    // Active Allergies Chips with Delete X
                    if (uiState.allergies.isEmpty()) {
                        Box(
                            modifier = Modifier
                                .fillMaxWidth()
                                .clip(RoundedCornerShape(8.dp))
                                .background(SoftMint.copy(alpha = 0.5f))
                                .padding(12.dp)
                        ) {
                            Text(
                                text = "No declared allergies on file. All recipes will pass allergen gating.",
                                style = MaterialTheme.typography.bodySmall.copy(color = ForestGreen)
                            )
                        }
                    } else {
                        FlowRow(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.spacedBy(8.dp),
                            verticalArrangement = Arrangement.spacedBy(6.dp)
                        ) {
                            uiState.allergies.forEach { allergen ->
                                SuggestionChip(
                                    onClick = { viewModel.removeAllergy(allergen) },
                                    label = {
                                        Text(
                                            "${allergen.replaceFirstChar { if (it.isLowerCase()) it.titlecase() else it.toString() }}  ✕",
                                            fontWeight = FontWeight.SemiBold
                                        )
                                    },
                                    colors = SuggestionChipDefaults.suggestionChipColors(
                                        containerColor = StatusAlertRedContainer,
                                        labelColor = StatusAlertRed
                                    ),
                                    border = SuggestionChipDefaults.suggestionChipBorder(
                                        enabled = true,
                                        borderColor = Color(0xFFFCA5A5)
                                    )
                                )
                            }
                        }
                    }

                    Spacer(modifier = Modifier.height(14.dp))
                    HorizontalDivider(color = Color(0xFFF1F5F9), thickness = 1.dp)
                    Spacer(modifier = Modifier.height(14.dp))

                    Text(
                        text = "Quick-add common allergens:",
                        style = MaterialTheme.typography.labelSmall.copy(color = TextSecondary)
                    )

                    FlowRow(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(vertical = 6.dp),
                        horizontalArrangement = Arrangement.spacedBy(6.dp),
                        verticalArrangement = Arrangement.spacedBy(4.dp)
                    ) {
                        commonAllergens.forEach { common ->
                            val alreadyAdded = uiState.allergies.any { it.equals(common, ignoreCase = true) }
                            SuggestionChip(
                                onClick = {
                                    if (!alreadyAdded) {
                                        viewModel.addAllergy(common)
                                    }
                                },
                                label = { Text(if (alreadyAdded) "✓ $common" else "+ $common", fontSize = 12.sp) },
                                colors = SuggestionChipDefaults.suggestionChipColors(
                                    containerColor = if (alreadyAdded) SoftMint else PureWhite,
                                    labelColor = if (alreadyAdded) ForestGreen else TextSecondary
                                )
                            )
                        }
                    }

                    Spacer(modifier = Modifier.height(10.dp))

                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.spacedBy(8.dp),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        OutlinedTextField(
                            value = newAllergenText,
                            onValueChange = { newAllergenText = it },
                            placeholder = { Text("e.g. seafood, sesame", fontSize = 13.sp) },
                            modifier = Modifier.weight(1f),
                            singleLine = true,
                            colors = OutlinedTextFieldDefaults.colors(
                                focusedBorderColor = ForestGreen,
                                focusedLabelColor = ForestGreen
                            )
                        )
                        Button(
                            onClick = {
                                if (newAllergenText.isNotBlank()) {
                                    viewModel.addAllergy(newAllergenText.trim())
                                    newAllergenText = ""
                                }
                            },
                            colors = ButtonDefaults.buttonColors(containerColor = ForestGreen),
                            shape = RoundedCornerShape(10.dp)
                        ) {
                            Icon(Icons.Default.Add, contentDescription = "Add")
                            Text("Add")
                        }
                    }
                }
            }

            Spacer(modifier = Modifier.height(20.dp))

            // Backend Connectivity Settings
            Card(
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(16.dp),
                colors = CardDefaults.cardColors(containerColor = PureWhite),
                elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
            ) {
                Column(modifier = Modifier.padding(18.dp)) {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            Icon(Icons.Default.Settings, contentDescription = null, tint = ForestGreen)
                            Text(
                                text = "FastAPI Backend Connection",
                                style = MaterialTheme.typography.titleMedium.copy(
                                    fontWeight = FontWeight.Bold,
                                    color = TextPrimary
                                ),
                                modifier = Modifier.padding(start = 8.dp)
                            )
                        }

                        Icon(
                            imageVector = if (uiState.isConnected == true) Icons.Default.CloudDone else Icons.Default.CloudOff,
                            contentDescription = null,
                            tint = if (uiState.isConnected == true) StatusSuccessGreen else StatusAlertRed,
                            modifier = Modifier.size(20.dp)
                        )
                    }

                    Text(
                        text = "Connects to your local laptop FastAPI server over Wi-Fi. Default port is 8000.",
                        style = MaterialTheme.typography.bodySmall.copy(color = TextSecondary),
                        modifier = Modifier.padding(top = 4.dp, bottom = 10.dp)
                    )

                    // Preset IP chips
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.spacedBy(6.dp)
                    ) {
                        networkPresets.forEach { (label, url) ->
                            SuggestionChip(
                                onClick = {
                                    backendUrlInput = url
                                    viewModel.updateBackendUrl(url)
                                },
                                label = { Text(label, fontSize = 11.sp) },
                                colors = SuggestionChipDefaults.suggestionChipColors(
                                    containerColor = if (uiState.backendUrl == url) SoftMint else PureWhite,
                                    labelColor = if (uiState.backendUrl == url) ForestGreen else TextSecondary
                                )
                            )
                        }
                    }

                    Spacer(modifier = Modifier.height(8.dp))

                    OutlinedTextField(
                        value = backendUrlInput,
                        onValueChange = { backendUrlInput = it },
                        label = { Text("Base URL") },
                        modifier = Modifier.fillMaxWidth(),
                        singleLine = true,
                        colors = OutlinedTextFieldDefaults.colors(
                            focusedBorderColor = ForestGreen,
                            focusedLabelColor = ForestGreen
                        )
                    )

                    Spacer(modifier = Modifier.height(14.dp))

                    Button(
                        onClick = {
                            viewModel.updateBackendUrl(backendUrlInput.trim())
                        },
                        colors = ButtonDefaults.buttonColors(containerColor = DarkForestGreen),
                        shape = RoundedCornerShape(10.dp),
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        if (uiState.isLoading) {
                            CircularProgressIndicator(
                                color = PureWhite,
                                modifier = Modifier.size(18.dp),
                                strokeWidth = 2.dp
                            )
                        } else {
                            Text("Save & Reconnect", fontWeight = FontWeight.Bold)
                        }
                    }

                    if (uiState.connectionStatusMessage.isNotBlank()) {
                        Spacer(modifier = Modifier.height(8.dp))
                        Text(
                            text = "Status: ${uiState.connectionStatusMessage}",
                            style = MaterialTheme.typography.bodySmall.copy(
                                color = if (uiState.isConnected == true) StatusSuccessGreen else StatusAlertRed
                            )
                        )
                    }
                }
            }

            Spacer(modifier = Modifier.height(24.dp))
        }
    }
}
