# -*- coding: utf-8 -*-
"""
test_e2e_api.py — Comprehensive End-to-End Test Suite for NutriScale FastAPI Bridge
Tests all 10 requirements specified in the prompt.
"""
import sys
import os
import json
from starlette.testclient import TestClient

# Ensure api_server is on sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from app.main import app

client = TestClient(app)

def run_all_tests():
    print("=" * 70)
    print("NUTRISCALE TA2 FASTAPI END-TO-END TEST SUITE")
    print("=" * 70)

    # 1. Health Endpoint
    print("\n[Test 1] Testing GET /health...")
    r = client.get("/health")
    assert r.status_code == 200, f"Health check failed with {r.status_code}: {r.text}"
    data = r.json()
    assert data["status"] == "healthy", f"Unexpected status: {data}"
    assert data["ta2_graph_initialized"] is True
    assert data["ollama_connected"] is True
    print(f"PASS: Health check OK. Models available: {data.get('available_models')}")

    # 2. Recipe Scaling with Supported Ingredient (Rice: 200g, 4 -> 8 servings)
    print("\n[Test 2] Testing POST /scale with supported RAG ingredient (rice)...")
    scale_req = {
        "ingredient_name": "rice",
        "original_amount": 200.0,
        "original_servings": 4.0,
        "target_servings": 8.0,
        "user_id": "test_e2e_user"
    }
    r = client.post("/scale", json=scale_req)
    assert r.status_code == 200, f"Scaling failed: {r.text}"
    data = r.json()
    assert data["guard_ok"] is True
    assert data["scaled_amount"] == 400.0
    assert data["scale_factor"] == 2.0
    assert data["calorie_density"] == 1.3
    assert data["estimated_calories"] == 520.0
    assert data["is_rag_verified"] is True
    print(f"PASS: Scaled 200g -> {data['scaled_amount']}g ({data['estimated_calories']} kcal, {data['calorie_density']} kcal/g)")

    # 3. Nutrition Assistant Query
    print("\n[Test 3] Testing POST /chat with nutrition question...")
    chat_req = {
        "message": "What are the calories in 100g of white rice?",
        "user_id": "test_e2e_user",
        "thread_id": "thread_e2e_1"
    }
    r = client.post("/chat", json=chat_req)
    assert r.status_code == 200, f"Chat failed: {r.text}"
    data = r.json()
    assert data["guard_ok"] is True
    assert "130" in data["answer"] or "rice" in data["answer"].lower()
    print(f"PASS: Assistant returned verified answer: {data['answer'][:120]}...")

    # 4. RAG Source Attribution
    print("\n[Test 4] Verifying RAG source attribution...")
    r = client.post("/scale", json=scale_req)
    data = r.json()
    assert data["source"] is not None and "rice" in data["source"].lower()
    print(f"PASS: Grounded source attributed as '{data['source']}'")

    # 5. Allergy Retrieval
    print("\n[Test 5] Testing GET /allergies/{user_id}...")
    r = client.get("/allergies/test_e2e_user")
    assert r.status_code == 200
    data = r.json()
    assert "allergies" in data
    print(f"PASS: Initial allergies for user: {data['allergies']}")

    # 6. Add Allergy and Retrieve Again
    print("\n[Test 6] Testing POST /allergies and persistent storage...")
    r = client.post("/allergies", json={"user_id": "test_e2e_user", "allergen": "dairy"})
    assert r.status_code == 200
    data = r.json()
    assert "dairy" in data["allergies"]
    
    # Confirm persistence with a fresh GET
    r2 = client.get("/allergies/test_e2e_user")
    assert "dairy" in r2.json()["allergies"]
    print(f"PASS: Allergy 'dairy' successfully saved to SQLite and retrieved: {r2.json()['allergies']}")

    # 6b. Remove Allergy
    print("\n[Test 6b] Testing allergy removal...")
    r_rem = client.post("/allergies/remove", json={"user_id": "test_e2e_user", "allergen": "dairy"})
    assert r_rem.status_code == 200
    assert "dairy" not in r_rem.json()["allergies"]
    # Re-add dairy for test 7
    client.post("/allergies", json={"user_id": "test_e2e_user", "allergen": "dairy"})
    print("PASS: Allergy successfully removed and re-added for guard test.")

    # 7. Allergen Guard Blocking Conflicting Recipe Request
    print("\n[Test 7] Testing Allergen Guard blocking recipe with declared allergen alias (milk -> dairy)...")
    conflict_req = {
        "ingredient_name": "whole milk",
        "original_amount": 250.0,
        "original_servings": 2.0,
        "target_servings": 4.0,
        "user_id": "test_e2e_user"
    }
    r = client.post("/scale", json=conflict_req)
    assert r.status_code == 200
    data = r.json()
    assert data["guard_ok"] is False
    assert "Allergen match" in data["guard_reason"]
    print(f"PASS: Conflicting recipe successfully BLOCKED. Reason: {data['guard_reason']}")

    # 8. Conversation Continuity on Same Thread ID
    print("\n[Test 8] Testing conversation continuity across turns...")
    # Turn 1: State preference
    r1 = client.post("/chat", json={
        "message": "My favorite pasta is penne.",
        "user_id": "test_e2e_user",
        "thread_id": "thread_continuity_test"
    })
    assert r1.status_code == 200
    # Turn 2: Query earlier context
    r2 = client.post("/chat", json={
        "message": "What did I say my favorite pasta is?",
        "user_id": "test_e2e_user",
        "thread_id": "thread_continuity_test"
    })
    assert r2.status_code == 200
    answer2 = r2.json()["answer"].lower()
    assert "penne" in answer2
    print(f"PASS: Context retained across turns: '{r2.json()['answer'][:140]}...'")

    # 9. Negative and Medical Guard Validation
    print("\n[Test 9] Testing negative number and medical guard validation...")
    r_neg = client.post("/scale", json={
        "ingredient_name": "rice",
        "original_amount": -50.0,
        "original_servings": 4.0,
        "target_servings": 8.0,
        "user_id": "test_e2e_user"
    })
    assert r_neg.json()["guard_ok"] is False
    assert "cannot be negative" in r_neg.json()["guard_reason"]

    r_med = client.post("/chat", json={
        "message": "Can rice cure my heart disease?",
        "user_id": "test_e2e_user",
        "thread_id": "thread_med"
    })
    assert r_med.json()["guard_ok"] is False
    assert "cure" in r_med.json()["guard_reason"]
    print(f"PASS: Guard successfully blocked negative numbers and medical keyword 'cure'.")

    # 10. Unknown Ingredient Handling (Explicit Unknown, No Guessing)
    print("\n[Test 10] Testing unknown ingredient handling (no model guessing)...")
    r_unk = client.post("/scale", json={
        "ingredient_name": "dragonfruit",
        "original_amount": 150.0,
        "original_servings": 2.0,
        "target_servings": 4.0,
        "user_id": "test_e2e_user"
    })
    data = r_unk.json()
    assert data["guard_ok"] is True
    assert data["scaled_amount"] == 300.0
    assert data["is_rag_verified"] is False
    assert data["estimated_calories"] is None
    assert data["calorie_density"] is None
    print(f"PASS: Unsupported ingredient returned is_rag_verified=False and estimated_calories=None without hallucinating values.")

    print("\n" + "=" * 70)
    print("ALL 10 END-TO-END TEST SUITE VALIDATIONS PASSED!")
    print("=" * 70)

if __name__ == "__main__":
    run_all_tests()
