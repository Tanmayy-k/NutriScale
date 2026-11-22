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
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.Calculate
import androidx.compose.material.icons.filled.CheckCircle
import androidx.compose.material.icons.filled.Info
import androidx.compose.material.icons.filled.MenuBook
import androidx.compose.material.icons.filled.Security
import androidx.compose.material.icons.filled.Shield
import androidx.compose.material.icons.filled.Verified
import androidx.compose.material.icons.filled.Warning
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.Divider
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.FilterChip
import androidx.compose.material3.FilterChipDefaults
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
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.nutriscale.app.data.models.ScaleResponse
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
fun RecipeScalerScreen(
    viewModel: NutriScaleViewModel,
    onBack: () -> Unit
) {
    val uiState by viewModel.uiState.collectAsState()
    var ingredient by remember { mutableStateOf("rice") }
    var origAmountText by remember { mutableStateOf("200") }
    var origServingsText by remember { mutableStateOf("4") }
    var targetServingsText by remember { mutableStateOf("8") }

    var latestResult by remember { mutableStateOf<ScaleResponse?>(null) }
    var validationError by remember { mutableStateOf<String?>(null) }

    val presetIngredients = listOf("rice", "chicken", "pasta", "wheat bread", "peanut butter")
    val presetServings = listOf(Pair("4", "8"), Pair("2", "4"), Pair("1", "3"))

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Recipe Scaler", fontWeight = FontWeight.Bold) },
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
            // Screen Header
            Text(
                text = "Deterministic Recipe Scaler",
                style = MaterialTheme.typography.titleLarge.copy(
                    fontWeight = FontWeight.Bold,
                    color = TextPrimary
                )
            )
            Text(
                text = "Grounded recipe scaling with pre-execution safety gating, local Chroma RAG calorie estimation, and independent critic verification.",
                style = MaterialTheme.typography.bodySmall.copy(color = TextSecondary),
                modifier = Modifier.padding(top = 4.dp, bottom = 14.dp)
            )

            // Input Parameters Card
            Card(
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(16.dp),
                colors = CardDefaults.cardColors(containerColor = PureWhite),
                elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
            ) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Text(
                        text = "Ingredient & Presets",
                        style = MaterialTheme.typography.labelLarge.copy(fontWeight = FontWeight.Bold, color = TextPrimary)
                    )

                    // Quick-preset chips for supported ingredients
                    FlowRow(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(vertical = 8.dp),
                        horizontalArrangement = Arrangement.spacedBy(6.dp),
                        verticalArrangement = Arrangement.spacedBy(4.dp)
                    ) {
                        presetIngredients.forEach { preset ->
                            val isSelected = ingredient.equals(preset, ignoreCase = true)
                            SuggestionChip(
                                onClick = { ingredient = preset },
                                label = { Text(preset) },
                                colors = SuggestionChipDefaults.suggestionChipColors(
                                    containerColor = if (isSelected) SoftMint else PureWhite,
                                    labelColor = if (isSelected) ForestGreen else TextSecondary
                                ),
                                border = SuggestionChipDefaults.suggestionChipBorder(
                                    enabled = true,
                                    borderColor = if (isSelected) ForestGreen else Color(0xFFE2E8F0)
                                )
                            )
                        }
                    }

                    OutlinedTextField(
                        value = ingredient,
                        onValueChange = { ingredient = it },
                        label = { Text("Ingredient Name") },
                        placeholder = { Text("e.g. rice, chicken breast, pasta") },
                        modifier = Modifier.fillMaxWidth(),
                        singleLine = true,
                        colors = OutlinedTextFieldDefaults.colors(
                            focusedBorderColor = ForestGreen,
                            focusedLabelColor = ForestGreen
                        )
                    )

                    Spacer(modifier = Modifier.height(12.dp))

                    OutlinedTextField(
                        value = origAmountText,
                        onValueChange = { origAmountText = it },
                        label = { Text("Original Quantity (grams)") },
                        keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
                        modifier = Modifier.fillMaxWidth(),
                        singleLine = true,
                        colors = OutlinedTextFieldDefaults.colors(
                            focusedBorderColor = ForestGreen,
                            focusedLabelColor = ForestGreen
                        )
                    )

                    Spacer(modifier = Modifier.height(14.dp))

                    Text(
                        text = "Servings Scaling Factor",
                        style = MaterialTheme.typography.labelLarge.copy(fontWeight = FontWeight.Bold, color = TextPrimary)
                    )

                    // Quick preset serving ratios
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(vertical = 6.dp),
                        horizontalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        presetServings.forEach { (orig, tgt) ->
                            val isSelected = origServingsText == orig && targetServingsText == tgt
                            SuggestionChip(
                                onClick = {
                                    origServingsText = orig
                                    targetServingsText = tgt
                                },
                                label = { Text("$orig → $tgt serv") },
                                colors = SuggestionChipDefaults.suggestionChipColors(
                                    containerColor = if (isSelected) SoftMint else PureWhite,
                                    labelColor = if (isSelected) ForestGreen else TextSecondary
                                )
                            )
                        }
                    }

                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.spacedBy(12.dp)
                    ) {
                        OutlinedTextField(
                            value = origServingsText,
                            onValueChange = { origServingsText = it },
                            label = { Text("Original Servings") },
                            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
                            modifier = Modifier.weight(1f),
                            singleLine = true,
                            colors = OutlinedTextFieldDefaults.colors(
                                focusedBorderColor = ForestGreen,
                                focusedLabelColor = ForestGreen
                            )
                        )
                        OutlinedTextField(
                            value = targetServingsText,
                            onValueChange = { targetServingsText = it },
                            label = { Text("Target Servings") },
                            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
                            modifier = Modifier.weight(1f),
                            singleLine = true,
                            colors = OutlinedTextFieldDefaults.colors(
                                focusedBorderColor = ForestGreen,
                                focusedLabelColor = ForestGreen
                            )
                        )
                    }

                    Spacer(modifier = Modifier.height(20.dp))

                    Button(
                        onClick = {
                            validationError = null
                            val amount = origAmountText.toDoubleOrNull()
                            val origServ = origServingsText.toDoubleOrNull()
                            val tgtServ = targetServingsText.toDoubleOrNull()

                            if (ingredient.isBlank()) {
                                validationError = "Please enter an ingredient name."
                            } else if (amount == null || amount <= 0) {
                                validationError = "Ingredient amount must be a positive number."
                            } else if (origServ == null || origServ <= 0 || tgtServ == null || tgtServ <= 0) {
                                validationError = "Servings must be positive numbers greater than zero."
                            } else {
                                viewModel.scaleRecipe(
                                    ingredient = ingredient.trim(),
                                    origAmount = amount,
                                    origServings = origServ,
                                    targetServings = tgtServ
                                ) { res ->
                                    latestResult = res
                                }
                            }
                        },
                        modifier = Modifier.fillMaxWidth(),
                        colors = ButtonDefaults.buttonColors(containerColor = ForestGreen),
                        shape = RoundedCornerShape(12.dp)
                    ) {
                        if (uiState.isLoading) {
                            CircularProgressIndicator(
                                color = PureWhite,
                                modifier = Modifier.size(20.dp),
                                strokeWidth = 2.dp
                            )
                        } else {
                            Icon(Icons.Default.Calculate, contentDescription = null, modifier = Modifier.padding(end = 8.dp))
                            Text("Scale Recipe & Verify Nutrition", fontWeight = FontWeight.Bold, fontSize = 15.sp)
                        }
                    }
                }
            }

            // Local Validation Error Banner
            validationError?.let { err ->
                Spacer(modifier = Modifier.height(14.dp))
                Card(
                    modifier = Modifier.fillMaxWidth(),
                    shape = RoundedCornerShape(12.dp),
                    colors = CardDefaults.cardColors(containerColor = StatusAlertRedContainer)
                ) {
                    Row(
                        modifier = Modifier.padding(14.dp),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Icon(Icons.Default.Warning, contentDescription = null, tint = StatusAlertRed)
                        Text(
                            text = err,
                            color = StatusAlertRed,
                            modifier = Modifier.padding(start = 10.dp),
                            style = MaterialTheme.typography.bodyMedium
                        )
                    }
                }
            }

            // Backend General Error Banner
            uiState.errorMessage?.let { err ->
                Spacer(modifier = Modifier.height(14.dp))
                Card(
                    modifier = Modifier.fillMaxWidth(),
                    shape = RoundedCornerShape(12.dp),
                    colors = CardDefaults.cardColors(containerColor = StatusAlertRedContainer)
                ) {
                    Row(
                        modifier = Modifier.padding(14.dp),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Icon(Icons.Default.Warning, contentDescription = null, tint = StatusAlertRed)
                        Text(
                            text = err,
                            color = StatusAlertRed,
                            modifier = Modifier.padding(start = 10.dp),
                            style = MaterialTheme.typography.bodyMedium
                        )
                    }
                }
            }

            // Results Card
            latestResult?.let { res ->
                Spacer(modifier = Modifier.height(20.dp))
                DetailedResultCard(res)
            }
        }
    }
}

@Composable
private fun DetailedResultCard(res: ScaleResponse) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(16.dp),
        colors = CardDefaults.cardColors(
            containerColor = if (res.guard_ok) StatusSuccessContainer else StatusAlertRedContainer
        ),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
    ) {
        Column(modifier = Modifier.padding(18.dp)) {
            // Header Pill
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Icon(
                        imageVector = if (res.guard_ok) Icons.Default.Shield else Icons.Default.Warning,
                        contentDescription = null,
                        tint = if (res.guard_ok) StatusSuccessGreen else StatusAlertRed,
                        modifier = Modifier.size(22.dp)
                    )
                    Text(
                        text = if (res.guard_ok) "Safety Guard: PASSED" else "Gated: BLOCKED by Allergen Guard",
                        style = MaterialTheme.typography.titleMedium.copy(
                            fontWeight = FontWeight.Bold,
                            color = if (res.guard_ok) StatusSuccessGreen else StatusAlertRed
                        ),
                        modifier = Modifier.padding(start = 8.dp)
                    )
                }

                if (res.guard_ok) {
                    Box(
                        modifier = Modifier
                            .clip(RoundedCornerShape(8.dp))
                            .background(ForestGreen)
                            .padding(horizontal = 8.dp, vertical = 4.dp)
                    ) {
                        Text(
                            text = "${res.scale_factor}× Factor",
                            color = PureWhite,
                            style = MaterialTheme.typography.bodySmall.copy(fontWeight = FontWeight.Bold)
                        )
                    }
                }
            }

            // Guard Reason (if blocked)
            if (!res.guard_ok) {
                Spacer(modifier = Modifier.height(10.dp))
                Text(
                    text = res.guard_reason ?: "Declared allergen conflict detected. Recipe scaling blocked.",
                    color = StatusAlertRed,
                    style = MaterialTheme.typography.bodyMedium.copy(fontWeight = FontWeight.SemiBold)
                )
                Text(
                    text = "No recipe scaling or calorie calculation was executed because safety policy prevents preparing meals containing declared allergens.",
                    color = TextSecondary,
                    style = MaterialTheme.typography.bodySmall,
                    modifier = Modifier.padding(top = 6.dp)
                )
            } else {
                Spacer(modifier = Modifier.height(14.dp))
                HorizontalDivider(color = Color(0xFFC6E2D0), thickness = 1.dp)
                Spacer(modifier = Modifier.height(14.dp))

                // Scaled Quantity & Servings Metrics
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween
                ) {
                    Column {
                        Text(
                            text = "Scaled Quantity",
                            style = MaterialTheme.typography.bodySmall.copy(color = TextSecondary)
                        )
                        Text(
                            text = "${res.scaled_amount} g",
                            style = MaterialTheme.typography.titleLarge.copy(
                                fontWeight = FontWeight.Bold,
                                color = TextPrimary
                            )
                        )
                        Text(
                            text = "Original: ${res.original_amount}g (${res.original_servings.toInt()} serv) → ${res.target_servings.toInt()} serv",
                            style = MaterialTheme.typography.bodySmall.copy(color = TextSecondary)
                        )
                    }

                    Column(horizontalAlignment = Alignment.End) {
                        Text(
                            text = "Total Energy",
                            style = MaterialTheme.typography.bodySmall.copy(color = TextSecondary)
                        )
                        Text(
                            text = res.estimated_calories?.let { "${it.toInt()} kcal" } ?: "UNKNOWN",
                            style = MaterialTheme.typography.titleLarge.copy(
                                fontWeight = FontWeight.Bold,
                                color = if (res.estimated_calories != null) ForestGreen else Color(0xFFD97706)
                            )
                        )
                        Text(
                            text = res.calorie_density?.let { "$it kcal/g" } ?: "No local reference",
                            style = MaterialTheme.typography.bodySmall.copy(color = TextSecondary)
                        )
                    }
                }

                Spacer(modifier = Modifier.height(14.dp))

                // RAG Source Citation Badge
                Box(
                    modifier = Modifier
                        .fillMaxWidth()
                        .clip(RoundedCornerShape(10.dp))
                        .background(PureWhite.copy(alpha = 0.8f))
                        .padding(horizontal = 12.dp, vertical = 8.dp)
                ) {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Icon(
                            imageVector = if (res.is_rag_verified) Icons.Default.Verified else Icons.Default.Info,
                            contentDescription = null,
                            tint = if (res.is_rag_verified) ForestGreen else Color(0xFFD97706),
                            modifier = Modifier.size(18.dp)
                        )
                        Text(
                            text = if (res.is_rag_verified) {
                                "RAG Grounded: ${res.source ?: "nutri_kb"} (${res.calorie_density} kcal/g)"
                            } else {
                                "Unknown Ingredient: Not found in local Chroma knowledge base"
                            },
                            style = MaterialTheme.typography.bodySmall.copy(
                                fontWeight = FontWeight.SemiBold,
                                color = if (res.is_rag_verified) ForestGreen else Color(0xFFD97706)
                            ),
                            modifier = Modifier.padding(start = 6.dp)
                        )
                    }
                }

                Spacer(modifier = Modifier.height(10.dp))

                // Independent Scaling Critic Audit Pill
                val expected = res.original_amount * (res.target_servings / res.original_servings)
                val diff = kotlin.math.abs(res.scaled_amount - expected)
                val criticPass = diff <= 0.05

                Box(
                    modifier = Modifier
                        .fillMaxWidth()
                        .clip(RoundedCornerShape(10.dp))
                        .background(PureWhite.copy(alpha = 0.8f))
                        .padding(horizontal = 12.dp, vertical = 8.dp)
                ) {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Column {
                            Text(
                                text = "Scaling Critic Audit",
                                style = MaterialTheme.typography.labelSmall.copy(
                                    fontWeight = FontWeight.Bold,
                                    color = TextSecondary
                                )
                            )
                            Text(
                                text = "Formula: ${res.original_amount} × (${res.target_servings.toInt()}/${res.original_servings.toInt()}) = ${String.format("%.2f", expected)}g",
                                style = MaterialTheme.typography.bodySmall.copy(color = TextSecondary)
                            )
                        }

                        Box(
                            modifier = Modifier
                                .clip(RoundedCornerShape(6.dp))
                                .background(if (criticPass) Color(0xFFDCFCE7) else StatusAlertRedContainer)
                                .padding(horizontal = 8.dp, vertical = 2.dp)
                        ) {
                            Text(
                                text = if (criticPass) "CRITIC: PASS" else "CRITIC: FAIL",
                                color = if (criticPass) StatusSuccessGreen else StatusAlertRed,
                                style = MaterialTheme.typography.labelSmall.copy(fontWeight = FontWeight.Bold)
                            )
                        }
                    }
                }
            }
        }
    }
}
