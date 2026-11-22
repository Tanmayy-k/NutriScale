# -*- coding: utf-8 -*-
"""
nutriscale_service.py — Direct Bridge to NutriScale TA2 Agents, RAG & Memory
Reuses existing prototype.py and ta2_tools.py without code duplication.
"""
import os
import sys
import json
import re
import urllib.request
import asyncio
from typing import Optional, List, Dict, Any

from app.core.config import TA2_DIR, TA1_DIR, OLLAMA_BASE_URL, OLLAMA_MODEL
from app.schemas import (
    HealthResponse,
    ScaleRequest,
    ScaleResponse,
    ChatRequest,
    ChatResponse,
    AllergyRequest,
    AllergyResponse,
)

# Insert TA2 and TA1 paths into sys.path
if TA2_DIR not in sys.path:
    sys.path.insert(0, TA2_DIR)
if TA1_DIR not in sys.path:
    sys.path.insert(0, TA1_DIR)

# Import existing TA2 components
from prototype import (
    graph as ta2_graph,
    run as run_ta2_graph,
    ltm_load,
    ltm_load_allergies,
    ltm_save,
    ltm_save_allergy,
    ALIASES,
    UNSAFE,
)
from ta2_tools import (
    scale_recipe,
    estimate_calories,
    rag_calories_per_unit,
    _get_vectorstore,
)


def check_ollama() -> tuple[bool, List[str]]:
    """Safely check Ollama connectivity without generating responses."""
    try:
        url = f"{OLLAMA_BASE_URL}/api/tags"
        req = urllib.request.Request(url, headers={"User-Agent": "NutriScaleAPI"})
        with urllib.request.urlopen(req, timeout=1.5) as resp:
            data = json.loads(resp.read().decode())
            models = [m.get("name", "") for m in data.get("models", [])]
            return True, models
    except Exception:
        return False, []


def check_health_service() -> HealthResponse:
    """Evaluate system readiness without modifying state or calling LLM."""
    ollama_ok, models = check_ollama()
    is_ready = ta2_graph is not None and ollama_ok
    status = "healthy" if is_ready else ("degraded" if ta2_graph is not None else "unhealthy")
    return HealthResponse(
        status=status,
        model=OLLAMA_MODEL,
        ollama_connected=ollama_ok,
        ta2_graph_initialized=(ta2_graph is not None),
        available_models=models,
    )


def check_allergen_for_ingredient(ingredient: str, stored_allergies: List[str]) -> tuple[bool, Optional[str]]:
    """
    Dedicated allergen guard check for recipe scaling.
    Uses stored allergies and culinary aliases from TA2 prototype.
    """
    words = [w.strip(".,!?;:\"'()[]{}").lower() for w in ingredient.split()]
    if any(k in words for k in ["unknown", "mystery", "unnamed"]):
        return False, "UNKNOWN: Ingredient is ambiguous; blocked pending clarification."

    ing_lower = ingredient.lower().strip()
    for allergen in stored_allergies:
        target_tokens = [allergen.lower()] + ALIASES.get(allergen.lower(), [])
        for token in target_tokens:
            if re.search(r'\b' + re.escape(token) + r'\b', ing_lower):
                return False, f"Allergen match: declared allergy '{allergen}' (matched '{token}') found in '{ingredient}'."
    return True, None


def scale_recipe_service(req: ScaleRequest) -> ScaleResponse:
    """
    Executes recipe scaling and grounded nutrition estimation.
    1. Validates inputs.
    2. Runs Allergen Guard against stored user allergies.
    3. Calculates deterministic scaled amounts.
    4. Retrieves verified calorie density from Chroma RAG.
    """
    so = req.original_servings
    st = req.target_servings
    oa = req.original_amount
    ing = req.ingredient_name.strip()
    user_id = req.user_id or "default"

    # Input validation
    if so <= 0 or st <= 0:
        return ScaleResponse(
            ingredient_name=ing,
            original_amount=oa,
            original_servings=so,
            target_servings=st,
            scale_factor=0.0,
            scaled_amount=0.0,
            guard_ok=False,
            guard_reason=f"Invalid servings: original ({so}) and target ({st}) must be > 0.",
        )
    if oa < 0:
        return ScaleResponse(
            ingredient_name=ing,
            original_amount=oa,
            original_servings=so,
            target_servings=st,
            scale_factor=st / so,
            scaled_amount=0.0,
            guard_ok=False,
            guard_reason=f"Invalid ingredient amount ({oa}): cannot be negative.",
        )

    # Allergen Guard checking stored SQLite allergies
    user_allergies = ltm_load_allergies(user_id)
    allergen_ok, allergen_reason = check_allergen_for_ingredient(ing, user_allergies)
    scale_factor = round(st / so, 4)
    scaled_amount = round(oa * (st / so), 2)

    if not allergen_ok:
        return ScaleResponse(
            ingredient_name=ing,
            original_amount=oa,
            original_servings=so,
            target_servings=st,
            scale_factor=scale_factor,
            scaled_amount=scaled_amount,
            guard_ok=False,
            guard_reason=allergen_reason,
        )

    # Grounded Nutrition RAG lookup
    cpu = rag_calories_per_unit(ing)
    if cpu is not None:
        estimated_calories = round(scaled_amount * cpu, 2)
        vs = _get_vectorstore()
        res = vs.similarity_search(ing + " calories per gram", k=1) if vs else []
        src = os.path.basename(res[0].metadata.get("source", "unknown")) if res else "nutri_kb"
        return ScaleResponse(
            ingredient_name=ing,
            original_amount=oa,
            original_servings=so,
            target_servings=st,
            scale_factor=scale_factor,
            scaled_amount=scaled_amount,
            estimated_calories=estimated_calories,
            calorie_density=cpu,
            is_rag_verified=True,
            source=src,
            guard_ok=True,
        )
    else:
        # Unknown ingredient in RAG -> Return UNKNOWN explicitly without guessing
        return ScaleResponse(
            ingredient_name=ing,
            original_amount=oa,
            original_servings=so,
            target_servings=st,
            scale_factor=scale_factor,
            scaled_amount=scaled_amount,
            estimated_calories=None,
            calorie_density=None,
            is_rag_verified=False,
            source=None,
            guard_ok=True,
        )


async def chat_service(req: ChatRequest) -> ChatResponse:
    """
    Executes the multi-agent LangGraph workflow via run_ta2_graph.
    Preserves Guard -> Allergen Guard -> Supervisor -> Agents.
    Executes asynchronously off the main event loop to protect FastAPI concurrency.
    """
    user_id = req.user_id or "default"
    thread_id = req.thread_id or f"thread_{user_id}"

    # Run graph in threadpool to prevent blocking the async event loop
    final = await asyncio.to_thread(
        run_ta2_graph,
        request=req.message,
        user_id=user_id,
        thread_id=thread_id,
    )

    return ChatResponse(
        answer=final.get("answer") or "No response generated.",
        guard_ok=bool(final.get("guard_ok", True)),
        guard_reason=final.get("guard_reason"),
        route=final.get("route"),
        trace=final.get("trace"),
    )


def get_allergies_service(user_id: str) -> AllergyResponse:
    """Retrieves declared allergies from persistent SQLite memory."""
    uid = user_id.strip() if user_id else "default"
    allergies = ltm_load_allergies(uid)
    return AllergyResponse(user_id=uid, allergies=allergies)


def add_allergy_service(user_id: str, allergen: str) -> AllergyResponse:
    """Stores a declared allergy in persistent SQLite memory and returns updated list."""
    uid = user_id.strip() if user_id else "default"
    al = allergen.strip().lower()
    if al:
        ltm_save_allergy(uid, al)
    allergies = ltm_load_allergies(uid)
    return AllergyResponse(user_id=uid, allergies=allergies)


def remove_allergy_service(user_id: str, allergen: str) -> AllergyResponse:
    """Removes a declared allergy from SQLite persistent memory and returns updated list."""
    import sqlite3
    uid = user_id.strip() if user_id else "default"
    al = allergen.strip().lower()
    if al:
        db_path = os.path.join(TA2_DIR, "memory.db")
        c = sqlite3.connect(db_path)
        c.execute("DELETE FROM allergies WHERE user_id=? AND allergen=?", (uid, al))
        c.commit()
        c.close()
    allergies = ltm_load_allergies(uid)
    return AllergyResponse(user_id=uid, allergies=allergies)
