package com.nutriscale.app.data.repository

import com.nutriscale.app.data.models.AllergyRequest
import com.nutriscale.app.data.models.AllergyResponse
import com.nutriscale.app.data.models.ChatRequest
import com.nutriscale.app.data.models.ChatResponse
import com.nutriscale.app.data.models.HealthResponse
import com.nutriscale.app.data.models.ScaleRequest
import com.nutriscale.app.data.models.ScaleResponse
import com.nutriscale.app.data.network.NetworkClient
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext

class NutriScaleRepository {

    suspend fun checkHealth(): NetworkResult<HealthResponse> = withContext(Dispatchers.IO) {
        try {
            val response = NetworkClient.getService().getHealth()
            if (response.isSuccessful && response.body() != null) {
                NetworkResult.Success(response.body()!!)
            } else {
                NetworkResult.Error("Backend returned error ${response.code()}: ${response.message()}", response.code())
            }
        } catch (e: Exception) {
            NetworkResult.Error("Cannot connect to backend at ${NetworkClient.getBaseUrl()}: ${e.localizedMessage ?: "Connection failed"}")
        }
    }

    suspend fun scaleRecipe(request: ScaleRequest): NetworkResult<ScaleResponse> = withContext(Dispatchers.IO) {
        try {
            val response = NetworkClient.getService().scaleRecipe(request)
            if (response.isSuccessful && response.body() != null) {
                NetworkResult.Success(response.body()!!)
            } else {
                NetworkResult.Error("Recipe scaling failed (${response.code()}): ${response.message()}", response.code())
            }
        } catch (e: Exception) {
            NetworkResult.Error("Network error: ${e.localizedMessage ?: "Unable to reach server"}")
        }
    }

    suspend fun sendChat(request: ChatRequest): NetworkResult<ChatResponse> = withContext(Dispatchers.IO) {
        try {
            val response = NetworkClient.getService().sendChat(request)
            if (response.isSuccessful && response.body() != null) {
                NetworkResult.Success(response.body()!!)
            } else {
                NetworkResult.Error("Assistant query failed (${response.code()}): ${response.message()}", response.code())
            }
        } catch (e: Exception) {
            NetworkResult.Error("Network error: ${e.localizedMessage ?: "Unable to reach server"}")
        }
    }

    suspend fun getAllergies(userId: String): NetworkResult<AllergyResponse> = withContext(Dispatchers.IO) {
        try {
            val response = NetworkClient.getService().getAllergies(userId)
            if (response.isSuccessful && response.body() != null) {
                NetworkResult.Success(response.body()!!)
            } else {
                NetworkResult.Error("Failed to fetch allergies (${response.code()}): ${response.message()}", response.code())
            }
        } catch (e: Exception) {
            NetworkResult.Error("Network error: ${e.localizedMessage ?: "Unable to reach server"}")
        }
    }

    suspend fun addAllergy(userId: String, allergen: String): NetworkResult<AllergyResponse> = withContext(Dispatchers.IO) {
        try {
            val response = NetworkClient.getService().addAllergy(AllergyRequest(user_id = userId, allergen = allergen))
            if (response.isSuccessful && response.body() != null) {
                NetworkResult.Success(response.body()!!)
            } else {
                NetworkResult.Error("Failed to record allergy (${response.code()}): ${response.message()}", response.code())
            }
        } catch (e: Exception) {
            NetworkResult.Error("Network error: ${e.localizedMessage ?: "Unable to reach server"}")
        }
    }

    suspend fun removeAllergy(userId: String, allergen: String): NetworkResult<AllergyResponse> = withContext(Dispatchers.IO) {
        try {
            val response = NetworkClient.getService().removeAllergy(AllergyRequest(user_id = userId, allergen = allergen))
            if (response.isSuccessful && response.body() != null) {
                NetworkResult.Success(response.body()!!)
            } else {
                NetworkResult.Error("Failed to remove allergy (${response.code()}): ${response.message()}", response.code())
            }
        } catch (e: Exception) {
            NetworkResult.Error("Network error: ${e.localizedMessage ?: "Unable to reach server"}")
        }
    }
}
