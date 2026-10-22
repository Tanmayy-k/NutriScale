# -*- coding: utf-8 -*-
"""
ta2_tools.py -- NutriScale TA2 Tool Definitions
================================================
Provides three LangChain @tool functions used by TA2 agents:
  1. scale_recipe           (preserved from TA1, unchanged)
  2. estimate_calories      (preserved from TA1, unchanged)
  3. retrieve_nutrition_info (NEW: RAG tool using Chroma + nomic-embed-text)

The RAG tool is initialised lazily; the Chroma collection is built from
documents in ta2/knowledge/ the first time it is needed.
"""

import os
import sys
import re

from langchain_core.tools import tool

# ── TA1 tools — unchanged logic, re-registered for TA2 ────────────────────────

@tool
def scale_recipe(
    servings_original: float,
    servings_target: float,
    ingredient_amount: float,
) -> str:
    """Scale an ingredient amount from its original serving count to a target serving count.
    Use FIRST when the user wants to scale a recipe.
    Args:
        servings_original: Original serving count (must be > 0).
        servings_target: Target serving count (must be > 0).
        ingredient_amount: Original ingredient amount (must be >= 0).
    """
    try:
        so = float(servings_original); st = float(servings_target); ia = float(ingredient_amount)
    except (TypeError, ValueError):
        return "ERROR: All inputs must be valid numbers."
    if so <= 0:
        return f"ERROR: servings_original must be > 0 (received {so})."
    if st <= 0:
        return f"ERROR: servings_target must be > 0 (received {st})."
    if ia < 0:
        return f"ERROR: ingredient_amount cannot be negative (received {ia})."
    factor = st / so
    scaled = ia * factor
    return (f"Scaled ingredient amount: {scaled:.2f} units "
            f"(original: {ia} units for {so} servings -> "
            f"{scaled:.2f} units for {st} servings, factor: {factor:.4f})")


@tool
def estimate_calories(
    ingredient_amount: float,
    calories_per_unit: float,
) -> str:
    """Estimate total calories for a given ingredient amount.
    Use AFTER scale_recipe; pass the scaled amount as ingredient_amount.
    Args:
        ingredient_amount: Amount of ingredient (must be >= 0).
        calories_per_unit: Calorie density per unit (must be >= 0).
    """
    try:
        ia = float(ingredient_amount); cpu = float(calories_per_unit)
    except (TypeError, ValueError):
        return "ERROR: All inputs must be valid numbers."
    if ia < 0:
        return f"ERROR: ingredient_amount cannot be negative (received {ia})."
    if cpu < 0:
        return f"ERROR: calories_per_unit cannot be negative (received {cpu})."
    total = ia * cpu
    return (f"Estimated calories: {total:.2f} kcal "
            f"({ia:.2f} units x {cpu} kcal/unit = {total:.2f} kcal)")


# ── RAG tool — Chroma + nomic-embed-text ──────────────────────────────────────

_vectorstore = None  # lazy singleton


def _get_vectorstore():
    """Build or load the Chroma vector store from knowledge documents."""
    global _vectorstore
    if _vectorstore is not None:
        return _vectorstore

    try:
        import chromadb
        from langchain_ollama import OllamaEmbeddings
        from langchain_community.vectorstores import Chroma
        from langchain_community.document_loaders import TextLoader
        from langchain_text_splitters import CharacterTextSplitter
    except ImportError as e:
        return None  # RAG unavailable — handled in tool

    # Paths
    here = os.path.dirname(os.path.abspath(__file__))
    kb_dir = os.path.join(here, "knowledge")
    db_dir = os.path.join(here, "chroma_db")

    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    splitter = CharacterTextSplitter(chunk_size=400, chunk_overlap=50)

    # Load and split documents
    docs = []
    for fname in os.listdir(kb_dir):
        if fname.endswith(".txt"):
            loader = TextLoader(os.path.join(kb_dir, fname), encoding="utf-8")
            raw = loader.load()
            chunks = splitter.split_documents(raw)
            docs.extend(chunks)

    if not docs:
        return None

    _vectorstore = Chroma.from_documents(
        documents=docs,
        embedding=embeddings,
        persist_directory=db_dir,
        collection_name="nutri_kb",
    )
    return _vectorstore


@tool
def retrieve_nutrition_info(query: str) -> str:
    """Retrieve reference nutrition information from the local knowledge base.
    Use for questions about calorie density, macronutrients, or serving sizes.
    Results are reference estimates, NOT medically precise facts.
    Args:
        query: The nutrition question or ingredient name to look up.
    """
    vs = _get_vectorstore()
    if vs is None:
        return ("RAG unavailable: knowledge base could not be loaded. "
                "Ensure Ollama is running and nomic-embed-text is pulled.")
    results = vs.similarity_search(query, k=2)
    if not results:
        return "No relevant nutrition information found in the knowledge base."
    parts = []
    for i, doc in enumerate(results, 1):
        source = os.path.basename(doc.metadata.get("source", "unknown"))
        parts.append(f"[Source: {source}]\n{doc.page_content.strip()}")
    return ("\n\n---\n\n".join(parts) +
            "\n\nDISCLAIMER: Reference estimates only, not medically precise.")


def rag_calories_per_unit(ingredient: str) -> float | None:
    """Retrieve calorie density (kcal per gram/unit) for an ingredient from knowledge base."""
    vs = _get_vectorstore()
    if vs is None or not ingredient:
        return None
    res = vs.similarity_search(ingredient + " calories per gram", k=1)
    if not res:
        return None
    doc = res[0]
    content = doc.page_content.lower()
    ing_clean = ingredient.lower().strip()
    if ing_clean not in content and not any(w in content for w in ing_clean.split() if len(w) > 2):
        return None
    m = re.search(r"(?:approximately|~)?\s*(\d+\.?\d*)\s*kcal per gram", doc.page_content, re.IGNORECASE)
    if m:
        try:
            return float(m.group(1))
        except (ValueError, TypeError):
            return None
    return None


@tool
def rag_scale_and_estimate(
    ingredient: str,
    original_amount: float,
    original_servings: float,
    target_servings: float,
) -> str:
    """Scale an ingredient and estimate calories using verified reference data from RAG.
    Use this to scale a recipe ingredient and calculate calories using verified knowledge base data.
    Args:
        ingredient: The ingredient name (e.g. 'rice', 'chicken').
        original_amount: Original ingredient amount in grams/units (> 0).
        original_servings: Original serving count (> 0).
        target_servings: Target serving count (> 0).
    """
    cpu = rag_calories_per_unit(ingredient)
    if cpu is None:
        return f"UNKNOWN: No calorie data found for '{ingredient}' in the knowledge base. Cannot estimate calories without a verified reference."
    try:
        oa = float(original_amount); os_ = float(original_servings); ts = float(target_servings)
    except (TypeError, ValueError):
        return "ERROR: All amounts and servings must be valid numbers."
    if os_ <= 0:
        return f"ERROR: original_servings must be > 0 (received {os_})."
    if ts <= 0:
        return f"ERROR: target_servings must be > 0 (received {ts})."
    if oa < 0:
        return f"ERROR: original_amount cannot be negative (received {oa})."

    scaled = oa * ts / os_
    total = scaled * cpu

    vs = _get_vectorstore()
    res = vs.similarity_search(ingredient + " calories per gram", k=1) if vs else []
    src = os.path.basename(res[0].metadata.get("source", "unknown")) if res else "unknown"

    return (f"[RAG-VERIFIED] Ingredient: {ingredient} | "
            f"Scaled amount: {scaled:.2f} units (original: {oa} for {os_} serv -> {ts} serv) | "
            f"Calorie density: {cpu} kcal/unit (source: {src}) | "
            f"Estimated calories: {total:.2f} kcal")

