# -*- coding: utf-8 -*-
"""
main.py — NutriScale FastAPI Application Server
Integrates Android Native Client with NutriScale TA2 Multi-Agent AI Backend.
"""
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.schemas import (
    HealthResponse,
    ScaleRequest,
    ScaleResponse,
    ChatRequest,
    ChatResponse,
    AllergyRequest,
    AllergyResponse,
)
from app.services.nutriscale_service import (
    check_health_service,
    scale_recipe_service,
    chat_service,
    get_allergies_service,
    add_allergy_service,
    remove_allergy_service,
)

app = FastAPI(
    title="NutriScale TA2 Mobile Gateway API",
    description="Local FastAPI bridge connecting NutriScale Android Client to TA2 Multi-Agent LangGraph System.",
    version="2.0.0",
)

# Enable CORS for local network and mobile devices
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse, tags=["Health"])
def get_health():
    """
    Check system health, LangGraph initialization, and Ollama connection status.
    Does not trigger LLM calls or mutate state.
    """
    return check_health_service()


@app.post("/scale", response_model=ScaleResponse, tags=["Recipe Scaler"])
def scale_recipe_endpoint(request: ScaleRequest):
    """
    Scales recipe ingredients and computes RAG-grounded calorie estimations.
    Enforces Allergen Guard and input validation.
    """
    try:
        return scale_recipe_service(request)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Scaling workflow error: {str(e)}",
        )


@app.post("/chat", response_model=ChatResponse, tags=["Nutrition Assistant"])
async def chat_endpoint(request: ChatRequest):
    """
    Executes the multi-agent LangGraph workflow.
    Preserves Guard, Supervisor, Recipe Agent, Nutrition Agent, and conversation memory.
    """
    try:
        return await chat_service(request)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Agent workflow error: {str(e)}",
        )


@app.get("/allergies/{user_id}", response_model=AllergyResponse, tags=["Allergies"])
def get_allergies(user_id: str):
    """
    Retrieves stored allergies for a specific user from SQLite persistent store.
    """
    try:
        return get_allergies_service(user_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to load allergies: {str(e)}",
        )


@app.post("/allergies/remove", response_model=AllergyResponse, tags=["Allergies"])
def remove_allergy_post(request: AllergyRequest):
    """
    Removes an allergen for user_id from SQLite persistent store (POST fallback for mobile clients).
    """
    try:
        return remove_allergy_service(request.user_id, request.allergen)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to remove allergy: {str(e)}",
        )


@app.delete("/allergies/{user_id}/{allergen}", response_model=AllergyResponse, tags=["Allergies"])
def delete_allergy_endpoint(user_id: str, allergen: str):
    """
    Removes an allergen for user_id from SQLite persistent store.
    """
    try:
        return remove_allergy_service(user_id, allergen)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to remove allergy: {str(e)}",
        )


@app.post("/allergies", response_model=AllergyResponse, tags=["Allergies"])
def add_allergy_body(request: AllergyRequest):
    """
    Saves an allergen for user_id in SQLite persistent store (body-only variation matching Android Retrofit).
    """
    try:
        return add_allergy_service(request.user_id, request.allergen)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to record allergy: {str(e)}",
        )


@app.post("/allergies/{user_id}", response_model=AllergyResponse, tags=["Allergies"])
def add_allergy_path(user_id: str, request: AllergyRequest):
    """
    Saves an allergen for user_id in SQLite persistent store (path parameter variation).
    """
    try:
        uid = user_id if user_id else request.user_id
        return add_allergy_service(uid, request.allergen)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to record allergy: {str(e)}",
        )
        return remove_allergy_service(request.user_id, request.allergen)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to remove allergy: {str(e)}",
        )
