package com.nutriscale.app.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.imePadding
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.lazy.rememberLazyListState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.automirrored.filled.Send
import androidx.compose.material.icons.filled.AutoAwesome
import androidx.compose.material.icons.filled.Psychology
import androidx.compose.material.icons.filled.Refresh
import androidx.compose.material.icons.filled.Security
import androidx.compose.material.icons.filled.Warning
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.ExperimentalMaterial3Api
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
import androidx.compose.runtime.LaunchedEffect
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
import com.nutriscale.app.ui.theme.TextPrimary
import com.nutriscale.app.ui.theme.TextSecondary
import com.nutriscale.app.viewmodel.ChatMessage
import com.nutriscale.app.viewmodel.NutriScaleViewModel

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun NutritionAssistantScreen(
    viewModel: NutriScaleViewModel,
    onBack: () -> Unit
) {
    val uiState by viewModel.uiState.collectAsState()
    var inputText by remember { mutableStateOf("") }
    val listState = rememberLazyListState()

    // Auto-scroll to latest message when new message arrives
    LaunchedEffect(uiState.chatMessages.size, uiState.isAssistantTyping) {
        if (uiState.chatMessages.isNotEmpty()) {
            listState.animateScrollToItem(uiState.chatMessages.size - 1)
        }
    }

    val sampleQueries = listOf(
        "What are the calories in 100g of white rice?",
        "Scale 200g of pasta from 4 to 8 servings.",
        "What are the macro benefits of chicken breast?"
    )

    Scaffold(
        topBar = {
            TopAppBar(
                title = {
                    Column {
                        Text("Nutrition Assistant", fontWeight = FontWeight.Bold, fontSize = 18.sp)
                        Text(
                            text = "LangGraph · Qwen2.5 · Chroma RAG",
                            fontSize = 11.sp,
                            color = PureWhite.copy(alpha = 0.85f)
                        )
                    }
                },
                navigationIcon = {
                    IconButton(onClick = onBack) {
                        Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = "Back", tint = PureWhite)
                    }
                },
                actions = {
                    IconButton(onClick = { viewModel.startNewConversation() }) {
                        Icon(Icons.Default.Refresh, contentDescription = "New Thread", tint = PureWhite)
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
        ) {
            // Chat message list
            LazyColumn(
                state = listState,
                modifier = Modifier
                    .weight(1f)
                    .fillMaxWidth(),
                contentPadding = PaddingValues(16.dp),
                verticalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                items(uiState.chatMessages, key = { it.id }) { message ->
                    ChatBubble(message = message)
                }

                if (uiState.isAssistantTyping) {
                    item {
                        TypingIndicatorBubble()
                    }
                }
            }

            // Quick suggestion chips
            if (uiState.chatMessages.size <= 2) {
                Column(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(horizontal = 16.dp, vertical = 4.dp)
                ) {
                    Text(
                        text = "Suggested queries:",
                        style = MaterialTheme.typography.bodySmall.copy(color = TextSecondary),
                        modifier = Modifier.padding(bottom = 4.dp)
                    )
                    sampleQueries.forEach { query ->
                        SuggestionChip(
                            onClick = {
                                viewModel.sendChatMessage(query)
                            },
                            label = { Text(query, fontSize = 12.sp) },
                            colors = SuggestionChipDefaults.suggestionChipColors(
                                containerColor = PureWhite,
                                labelColor = ForestGreen
                            ),
                            modifier = Modifier.padding(bottom = 4.dp)
                        )
                    }
                }
            }

            // Bottom Input Bar
            Card(
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(topStart = 16.dp, topEnd = 16.dp),
                colors = CardDefaults.cardColors(containerColor = PureWhite),
                elevation = CardDefaults.cardElevation(defaultElevation = 6.dp)
            ) {
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(horizontal = 12.dp, vertical = 10.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    OutlinedTextField(
                        value = inputText,
                        onValueChange = { inputText = it },
                        placeholder = { Text("Ask about recipe scaling or nutrition...", fontSize = 14.sp) },
                        modifier = Modifier.weight(1f),
                        maxLines = 3,
                        shape = RoundedCornerShape(24.dp),
                        colors = OutlinedTextFieldDefaults.colors(
                            focusedBorderColor = ForestGreen,
                            unfocusedBorderColor = Color(0xFFCBD5E1)
                        )
                    )

                    Spacer(modifier = Modifier.width(8.dp))

                    IconButton(
                        onClick = {
                            if (inputText.isNotBlank() && !uiState.isAssistantTyping) {
                                val text = inputText.trim()
                                inputText = ""
                                viewModel.sendChatMessage(text)
                            }
                        },
                        enabled = inputText.isNotBlank() && !uiState.isAssistantTyping,
                        modifier = Modifier
                            .size(48.dp)
                            .clip(CircleShape)
                            .background(if (inputText.isNotBlank()) ForestGreen else Color(0xFFE2E8F0))
                    ) {
                        Icon(
                            imageVector = Icons.AutoMirrored.Filled.Send,
                            contentDescription = "Send",
                            tint = if (inputText.isNotBlank()) PureWhite else Color(0xFF94A3B8)
                        )
                    }
                }
            }
        }
    }
}

@Composable
private fun ChatBubble(message: ChatMessage) {
    val isUser = message.isUser

    Row(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = if (isUser) Arrangement.End else Arrangement.Start
    ) {
        if (!isUser) {
            Box(
                modifier = Modifier
                    .size(32.dp)
                    .clip(CircleShape)
                    .background(SoftMint),
                contentAlignment = Alignment.Center
            ) {
                Icon(
                    imageVector = if (message.isBlocked) Icons.Default.Security else Icons.Default.AutoAwesome,
                    contentDescription = null,
                    tint = if (message.isBlocked) StatusAlertRed else ForestGreen,
                    modifier = Modifier.size(18.dp)
                )
            }
            Spacer(modifier = Modifier.width(8.dp))
        }

        Card(
            modifier = Modifier.fillMaxWidth(0.82f),
            shape = RoundedCornerShape(
                topStart = 16.dp,
                topEnd = 16.dp,
                bottomStart = if (isUser) 16.dp else 4.dp,
                bottomEnd = if (isUser) 4.dp else 16.dp
            ),
            colors = CardDefaults.cardColors(
                containerColor = when {
                    isUser -> ForestGreen
                    message.isBlocked -> StatusAlertRedContainer
                    else -> PureWhite
                }
            ),
            elevation = CardDefaults.cardElevation(defaultElevation = 1.dp)
        ) {
            Column(modifier = Modifier.padding(12.dp)) {
                if (!isUser) {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Text(
                            text = if (message.isBlocked) "Safety Guard" else "NutriScale Agent",
                            style = MaterialTheme.typography.labelSmall.copy(
                                fontWeight = FontWeight.Bold,
                                color = if (message.isBlocked) StatusAlertRed else ForestGreen
                            )
                        )
                        message.route?.let { route ->
                            Box(
                                modifier = Modifier
                                    .clip(RoundedCornerShape(4.dp))
                                    .background(SoftMint)
                                    .padding(horizontal = 6.dp, vertical = 2.dp)
                            ) {
                                Text(
                                    text = "Route: $route",
                                    fontSize = 10.sp,
                                    color = DarkForestGreen,
                                    fontWeight = FontWeight.Medium
                                )
                            }
                        }
                    }
                    Spacer(modifier = Modifier.height(4.dp))
                }

                Text(
                    text = message.text,
                    style = MaterialTheme.typography.bodyMedium.copy(
                        color = if (isUser) PureWhite else if (message.isBlocked) StatusAlertRed else TextPrimary,
                        lineHeight = 20.sp
                    )
                )

                if (message.blockReason != null) {
                    Spacer(modifier = Modifier.height(6.dp))
                    Text(
                        text = "Reason: ${message.blockReason}",
                        style = MaterialTheme.typography.bodySmall.copy(
                            color = StatusAlertRed,
                            fontWeight = FontWeight.SemiBold
                        )
                    )
                }
            }
        }
    }
}

@Composable
private fun TypingIndicatorBubble() {
    Row(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.Start,
        verticalAlignment = Alignment.CenterVertically
    ) {
        Box(
            modifier = Modifier
                .size(32.dp)
                .clip(CircleShape)
                .background(SoftMint),
            contentAlignment = Alignment.Center
        ) {
            Icon(Icons.Default.Psychology, contentDescription = null, tint = ForestGreen, modifier = Modifier.size(18.dp))
        }
        Spacer(modifier = Modifier.width(8.dp))
        Card(
            shape = RoundedCornerShape(16.dp),
            colors = CardDefaults.cardColors(containerColor = PureWhite),
            elevation = CardDefaults.cardElevation(defaultElevation = 1.dp)
        ) {
            Row(
                modifier = Modifier.padding(horizontal = 14.dp, vertical = 10.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                CircularProgressIndicator(
                    color = ForestGreen,
                    modifier = Modifier.size(16.dp),
                    strokeWidth = 2.dp
                )
                Text(
                    text = "Qwen2.5 & Chroma RAG are thinking...",
                    style = MaterialTheme.typography.bodySmall.copy(color = TextSecondary),
                    modifier = Modifier.padding(start = 10.dp)
                )
            }
        }
    }
}
