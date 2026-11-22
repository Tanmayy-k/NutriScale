package com.nutriscale.app.data.models

data class ScaleRequest(
    val ingredient_name: String,
    val original_amount: Double,
    val original_servings: Double,
    val target_servings: Double,
    val user_id: String = "default"
)

data class ScaleResponse(
    val ingredient_name: String,
    val original_amount: Double,
    val original_servings: Double,
    val target_servings: Double,
    val scale_factor: Double,
    val scaled_amount: Double,
    val estimated_calories: Double?,
    val calorie_density: Double?,
    val is_rag_verified: Boolean = false,
    val source: String? = null,
    val guard_ok: Boolean = true,
    val guard_reason: String? = null
)

data class ChatRequest(
    val message: String,
    val user_id: String = "default",
    val thread_id: String? = null
)

data class ChatResponse(
    val answer: String,
    val guard_ok: Boolean,
    val guard_reason: String?,
    val route: String?,
    val trace: List<Map<String, Any>>? = null
)

data class AllergyRequest(
    val user_id: String,
    val allergen: String
)

data class AllergyResponse(
    val user_id: String,
    val allergies: List<String>
)

data class HealthResponse(
    val status: String,
    val model: String?,
    val ollama_connected: Boolean
)
