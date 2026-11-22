# -*- coding: utf-8 -*-
"""
schemas.py — NutriScale Pydantic Schemas
Strictly aligned with Android Retrofit models in ApiModels.kt
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


# ── Health ────────────────────────────────────────────────────────────────────
class HealthResponse(BaseModel):
    status: str
    model: Optional[str] = None
    ollama_connected: bool = False
    ta2_graph_initialized: bool = True
    available_models: List[str] = Field(default_factory=list)


# ── Recipe Scaling ────────────────────────────────────────────────────────────
class ScaleRequest(BaseModel):
    ingredient_name: str
    original_amount: float
    original_servings: float
    target_servings: float
    user_id: str = "default"


class ScaleResponse(BaseModel):
    ingredient_name: str
    original_amount: float
    original_servings: float
    target_servings: float
    scale_factor: float
    scaled_amount: float
    estimated_calories: Optional[float] = None
    calorie_density: Optional[float] = None
    is_rag_verified: bool = False
    source: Optional[str] = None
    guard_ok: bool = True
    guard_reason: Optional[str] = None


# ── Nutrition Assistant (Chat) ────────────────────────────────────────────────
class ChatRequest(BaseModel):
    message: str
    user_id: str = "default"
    thread_id: Optional[str] = None


class ChatResponse(BaseModel):
    answer: str
    guard_ok: bool
    guard_reason: Optional[str] = None
    route: Optional[str] = None
    trace: Optional[List[Dict[str, Any]]] = None


# ── Allergies & Preferences ───────────────────────────────────────────────────
class AllergyRequest(BaseModel):
    user_id: str = "default"
    allergen: str


class AllergyResponse(BaseModel):
    user_id: str
    allergies: List[str] = Field(default_factory=list)
