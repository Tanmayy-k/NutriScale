package com.nutriscale.app.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.nutriscale.app.data.models.ChatRequest
import com.nutriscale.app.data.models.ScaleRequest
import com.nutriscale.app.data.models.ScaleResponse
import com.nutriscale.app.data.network.NetworkClient
import com.nutriscale.app.data.repository.NetworkResult
import com.nutriscale.app.data.repository.NutriScaleRepository
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

data class ChatMessage(
    val id: String = java.util.UUID.randomUUID().toString(),
    val isUser: Boolean,
    val text: String,
    val isBlocked: Boolean = false,
    val blockReason: String? = null,
    val route: String? = null,
    val timestamp: Long = System.currentTimeMillis()
)

data class HomeUiState(
    val userId: String = "demo_user",
    val backendUrl: String = NetworkClient.getBaseUrl(),
    val isConnected: Boolean? = null,
    val modelName: String? = null,
    val connectionStatusMessage: String = "Not connected yet",
    val allergies: List<String> = emptyList(),
    // Daily Nutrition Target & Actual Metrics
    val consumedCalories: Int = 1420,
    val targetCalories: Int = 2100,
    val proteinGrams: Int = 92,
    val targetProteinGrams: Int = 140,
    val carbsGrams: Int = 165,
    val targetCarbsGrams: Int = 220,
    val fatGrams: Int = 42,
    val targetFatGrams: Int = 65,
    val recentActivity: List<ScaleResponse> = emptyList(),
    val isLoading: Boolean = false,
    val errorMessage: String? = null,
    // Assistant Conversation State
    val chatThreadId: String = "thread_demo_${System.currentTimeMillis() / 1000}",
    val chatMessages: List<ChatMessage> = listOf(
        ChatMessage(
            isUser = false,
            text = "Hello! I am your NutriScale AI Assistant. Ask me about ingredient nutrition, calorie densities, or recipe scaling."
        )
    ),
    val isAssistantTyping: Boolean = false
)

class NutriScaleViewModel(
    private val repository: NutriScaleRepository = NutriScaleRepository()
) : ViewModel() {

    private val _uiState = MutableStateFlow(HomeUiState())
    val uiState: StateFlow<HomeUiState> = _uiState.asStateFlow()

    init {
        checkBackendHealth()
        loadAllergies()
    }

    fun updateBackendUrl(url: String) {
        val sanitized = if (url.endsWith("/")) url else "$url/"
        NetworkClient.setBaseUrl(sanitized)
        _uiState.value = _uiState.value.copy(backendUrl = NetworkClient.getBaseUrl())
        checkBackendHealth()
        loadAllergies()
    }

    fun clearErrorMessage() {
        _uiState.value = _uiState.value.copy(errorMessage = null)
    }

    fun checkBackendHealth() {
        viewModelScope.launch {
            _uiState.value = _uiState.value.copy(isLoading = true, errorMessage = null)
            when (val result = repository.checkHealth()) {
                is NetworkResult.Success -> {
                    _uiState.value = _uiState.value.copy(
                        isConnected = true,
                        modelName = result.data.model ?: "qwen2.5:3b",
                        connectionStatusMessage = "Backend online (Ollama: ${if (result.data.ollama_connected) "Connected" else "Offline"})",
                        isLoading = false
                    )
                }
                is NetworkResult.Error -> {
                    _uiState.value = _uiState.value.copy(
                        isConnected = false,
                        modelName = null,
                        connectionStatusMessage = result.message,
                        isLoading = false
                    )
                }
                is NetworkResult.Loading -> {}
            }
        }
    }

    fun loadAllergies() {
        viewModelScope.launch {
            when (val result = repository.getAllergies(_uiState.value.userId)) {
                is NetworkResult.Success -> {
                    _uiState.value = _uiState.value.copy(allergies = result.data.allergies)
                }
                is NetworkResult.Error -> {
                    // Silently preserve current list if disconnected
                }
                is NetworkResult.Loading -> {}
            }
        }
    }

    fun addAllergy(allergen: String) {
        val trimmed = allergen.trim().lowercase()
        if (trimmed.isBlank()) return
        viewModelScope.launch {
            _uiState.value = _uiState.value.copy(isLoading = true)
            when (val result = repository.addAllergy(_uiState.value.userId, trimmed)) {
                is NetworkResult.Success -> {
                    _uiState.value = _uiState.value.copy(
                        allergies = result.data.allergies,
                        isLoading = false
                    )
                }
                is NetworkResult.Error -> {
                    _uiState.value = _uiState.value.copy(
                        errorMessage = result.message,
                        isLoading = false
                    )
                }
                is NetworkResult.Loading -> {}
            }
        }
    }

    fun removeAllergy(allergen: String) {
        val trimmed = allergen.trim().lowercase()
        if (trimmed.isBlank()) return
        viewModelScope.launch {
            _uiState.value = _uiState.value.copy(isLoading = true)
            when (val result = repository.removeAllergy(_uiState.value.userId, trimmed)) {
                is NetworkResult.Success -> {
                    _uiState.value = _uiState.value.copy(
                        allergies = result.data.allergies,
                        isLoading = false
                    )
                }
                is NetworkResult.Error -> {
                    _uiState.value = _uiState.value.copy(
                        errorMessage = result.message,
                        isLoading = false
                    )
                }
                is NetworkResult.Loading -> {}
            }
        }
    }

    fun scaleRecipe(
        ingredient: String,
        origAmount: Double,
        origServings: Double,
        targetServings: Double,
        onResult: (ScaleResponse) -> Unit = {}
    ) {
        viewModelScope.launch {
            _uiState.value = _uiState.value.copy(isLoading = true, errorMessage = null)
            val req = ScaleRequest(
                ingredient_name = ingredient,
                original_amount = origAmount,
                original_servings = origServings,
                target_servings = targetServings,
                user_id = _uiState.value.userId
            )
            when (val result = repository.scaleRecipe(req)) {
                is NetworkResult.Success -> {
                    val updatedList = listOf(result.data) + _uiState.value.recentActivity
                    _uiState.value = _uiState.value.copy(
                        recentActivity = updatedList,
                        isLoading = false
                    )
                    onResult(result.data)
                }
                is NetworkResult.Error -> {
                    _uiState.value = _uiState.value.copy(
                        isLoading = false,
                        errorMessage = result.message
                    )
                }
                is NetworkResult.Loading -> {}
            }
        }
    }

    fun sendChatMessage(userText: String) {
        val prompt = userText.trim()
        if (prompt.isBlank()) return

        val userMsg = ChatMessage(isUser = true, text = prompt)
        val updatedMessages = _uiState.value.chatMessages + userMsg
        _uiState.value = _uiState.value.copy(
            chatMessages = updatedMessages,
            isAssistantTyping = true,
            errorMessage = null
        )

        viewModelScope.launch {
            val req = ChatRequest(
                message = prompt,
                user_id = _uiState.value.userId,
                thread_id = _uiState.value.chatThreadId
            )
            when (val result = repository.sendChat(req)) {
                is NetworkResult.Success -> {
                    val botMsg = ChatMessage(
                        isUser = false,
                        text = result.data.answer,
                        isBlocked = !result.data.guard_ok,
                        blockReason = result.data.guard_reason,
                        route = result.data.route
                    )
                    _uiState.value = _uiState.value.copy(
                        chatMessages = _uiState.value.chatMessages + botMsg,
                        isAssistantTyping = false
                    )
                }
                is NetworkResult.Error -> {
                    val errMsg = ChatMessage(
                        isUser = false,
                        text = "Connection error: ${result.message}\nPlease check that FastAPI is running and reachable at ${_uiState.value.backendUrl}",
                        isBlocked = true,
                        blockReason = "Network Error"
                    )
                    _uiState.value = _uiState.value.copy(
                        chatMessages = _uiState.value.chatMessages + errMsg,
                        isAssistantTyping = false
                    )
                }
                is NetworkResult.Loading -> {}
            }
        }
    }

    fun startNewConversation() {
        val newThreadId = "thread_demo_${System.currentTimeMillis() / 1000}"
        _uiState.value = _uiState.value.copy(
            chatThreadId = newThreadId,
            chatMessages = listOf(
                ChatMessage(
                    isUser = false,
                    text = "New conversation started. Context has been reset. How can I help you today?"
                )
            )
        )
    }
}
