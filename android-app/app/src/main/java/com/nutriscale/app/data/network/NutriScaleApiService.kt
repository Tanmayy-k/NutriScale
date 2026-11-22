package com.nutriscale.app.data.network

import com.nutriscale.app.data.models.AllergyRequest
import com.nutriscale.app.data.models.AllergyResponse
import com.nutriscale.app.data.models.ChatRequest
import com.nutriscale.app.data.models.ChatResponse
import com.nutriscale.app.data.models.HealthResponse
import com.nutriscale.app.data.models.ScaleRequest
import com.nutriscale.app.data.models.ScaleResponse
import retrofit2.Response
import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.POST
import retrofit2.http.Path

interface NutriScaleApiService {

    @GET("health")
    suspend fun getHealth(): Response<HealthResponse>

    @POST("chat")
    suspend fun sendChat(
        @Body request: ChatRequest
    ): Response<ChatResponse>

    @POST("scale")
    suspend fun scaleRecipe(
        @Body request: ScaleRequest
    ): Response<ScaleResponse>

    @GET("allergies/{user_id}")
    suspend fun getAllergies(
        @Path("user_id") userId: String
    ): Response<AllergyResponse>

    @POST("allergies")
    suspend fun addAllergy(
        @Body request: AllergyRequest
    ): Response<AllergyResponse>

    @POST("allergies/remove")
    suspend fun removeAllergy(
        @Body request: AllergyRequest
    ): Response<AllergyResponse>
}
