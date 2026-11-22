package com.nutriscale.app.data.network

import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import java.util.concurrent.TimeUnit

object NetworkClient {

    // Default emulator host address mapping to host machine's 127.0.0.1
    const val DEFAULT_EMULATOR_URL = "http://10.0.2.2:8000/"
    const val DEFAULT_LOCAL_URL = "http://127.0.0.1:8000/"

    private var currentBaseUrl: String = DEFAULT_EMULATOR_URL
    private var apiService: NutriScaleApiService? = null

    fun setBaseUrl(newUrl: String) {
        val sanitized = if (newUrl.endsWith("/")) newUrl else "$newUrl/"
        if (sanitized != currentBaseUrl) {
            currentBaseUrl = sanitized
            apiService = null
        }
    }

    fun getBaseUrl(): String = currentBaseUrl

    fun getService(): NutriScaleApiService {
        return apiService ?: synchronized(this) {
            apiService ?: createRetrofitService(currentBaseUrl).also { apiService = it }
        }
    }

    private fun createRetrofitService(baseUrl: String): NutriScaleApiService {
        val logging = HttpLoggingInterceptor().apply {
            level = HttpLoggingInterceptor.Level.BODY
        }

        val okHttpClient = OkHttpClient.Builder()
            .addInterceptor(logging)
            .connectTimeout(15, TimeUnit.SECONDS)
            .readTimeout(30, TimeUnit.SECONDS)
            .writeTimeout(15, TimeUnit.SECONDS)
            .build()

        return Retrofit.Builder()
            .baseUrl(baseUrl)
            .client(okHttpClient)
            .addConverterFactory(GsonConverterFactory.create())
            .build()
            .create(NutriScaleApiService::class.java)
    }
}
