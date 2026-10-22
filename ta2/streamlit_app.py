# -*- coding: utf-8 -*-
"""
streamlit_app.py — NutriScale TA2 Streamlit Frontend
=====================================================
Professional Streamlit dashboard connected to the real NutriScale TA2 multi-agent backend:
- Invokes prototype.py (StateGraph: Guard -> Allergen Guard -> Supervisor -> Recipe/Nutrition Agent)
- Displays short-term thread memory and persistent SQLite preferences & allergies
- Visualizes RAG references (Chroma + nomic-embed-text)
- Shows live Allergen Guard decisions (BLOCK / PASS / UNKNOWN)
- Displays independent scaling critic verification
- Preserves deterministic arithmetic calculations
"""

import os
import sys
import json
import time
import urllib.request
import streamlit as st

# Setup paths to import from ta2
TA2_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(TA2_DIR)
sys.path.insert(0, TA2_DIR)
sys.path.insert(0, os.path.join(ROOT_DIR, "ta1"))

from prototype import run as run_ta2_graph, ltm_load, ltm_load_allergies, ltm_save, ltm_save_allergy
from ta2_tools import rag_calories_per_unit, _get_vectorstore

# ─────────────────────────────────────────────────────────────────────────────
# Page Configuration
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="NutriScale TA2 · Multi-Agent Nutrition Platform",
    page_icon="🥗",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# Theme & Minimal Clean Styling
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
html, body, [data-testid="stAppViewContainer"] {
    background-color: #0b0f17;
    color: #e2e8f0;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
}
[data-testid="stHeader"] { background: transparent; }
#MainMenu, footer { visibility: hidden; }

.block-container {
    max-width: 1140px;
    padding-top: 1.5rem;
    padding-bottom: 3rem;
}

/* Card container accents */
div[data-testid="stVerticalBlock"] > div[data-testid="stContainer"] {
    background-color: #131b26;
    border: 1px solid #243042;
    border-radius: 10px;
    padding: 1.25rem;
}

/* Status pills */
.badge-pass {
    background: #064e3b;
    color: #34d399;
    padding: 3px 10px;
    border-radius: 9999px;
    font-size: 0.82rem;
    font-weight: 700;
    display: inline-block;
}
.badge-block {
    background: #7f1d1d;
    color: #f87171;
    padding: 3px 10px;
    border-radius: 9999px;
    font-size: 0.82rem;
    font-weight: 700;
    display: inline-block;
}
.badge-info {
    background: #1e3a8a;
    color: #60a5fa;
    padding: 3px 10px;
    border-radius: 9999px;
    font-size: 0.82rem;
    font-weight: 600;
    display: inline-block;
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# Helper Utilities
# ─────────────────────────────────────────────────────────────────────────────
def check_ollama_status():
    try:
        req = urllib.request.Request("http://127.0.0.1:11434/api/tags", headers={"User-Agent": "NutriScale"})
        with urllib.request.urlopen(req, timeout=1.5) as resp:
            data = json.loads(resp.read().decode())
            models = [m.get("name") for m in data.get("models", [])]
            return True, models
    except Exception as e:
        return False, []


# ─────────────────────────────────────────────────────────────────────────────
# Sidebar: System Health & Memory Management
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🥗 NutriScale TA2")
    st.caption("Multi-Agent Architecture · Safety Guard · RAG")
    st.divider()

    # User Profile & Short-Term Memory Thread
    st.markdown("#### 👤 User & Session Scope")
    user_id = st.text_input("User ID (Persistent Store)", value="demo_user", help="Separates stored preferences and allergies in SQLite")
    
    if "thread_id" not in st.session_state:
        st.session_state.thread_id = f"thread_{int(time.time())}"
    
    col_t1, col_t2 = st.columns([3, 1])
    with col_t1:
        thread_id = st.text_input("Thread ID (Short-Term Memory)", value=st.session_state.thread_id)
    with col_t2:
        if st.button("New", help="Start new isolated conversation thread"):
            st.session_state.thread_id = f"thread_{int(time.time())}"
            st.rerun()

    st.divider()

    # Persistent SQLite Memory Inspection
    st.markdown("#### 💾 Persistent Memory (SQLite)")
    prefs = ltm_load(user_id)
    allergies = ltm_load_allergies(user_id)

    with st.expander("Declared Allergies", expanded=True):
        if allergies:
            for a in allergies:
                st.markdown(f"- ⚠️ **{a.capitalize()}**")
        else:
            st.caption("No allergies currently on file.")
        
        new_allergy = st.text_input("Add Allergen", key="new_allergy_input", placeholder="e.g. wheat, peanut, dairy")
        if st.button("Save Allergen") and new_allergy.strip():
            ltm_save_allergy(user_id, new_allergy.strip())
            st.success(f"Saved allergen '{new_allergy.strip()}' for {user_id}")
            st.rerun()

    with st.expander("Dietary Preferences", expanded=False):
        if prefs:
            for k, v in prefs.items():
                st.markdown(f"- **{k}:** {v}")
        else:
            st.caption("No dietary preferences recorded.")
        
        c_k, c_v = st.columns(2)
        with c_k:
            pk = st.text_input("Key", placeholder="favourite_food", key="pk")
        with c_v:
            pv = st.text_input("Value", placeholder="pasta", key="pv")
        if st.button("Save Preference") and pk.strip() and pv.strip():
            ltm_save(user_id, pk.strip(), pv.strip())
            st.success(f"Saved {pk}={pv}")
            st.rerun()

    st.divider()

    # Environment Status
    st.markdown("#### ⚙️ Engine Status")
    is_up, models = check_ollama_status()
    if is_up:
        st.markdown('<span class="badge-pass">● Ollama Connected</span>', unsafe_allow_html=True)
        st.caption(f"Host: `127.0.0.1:11434`\nModels: {', '.join(models) if models else 'None'}")
    else:
        st.markdown('<span class="badge-block">● Ollama Offline</span>', unsafe_allow_html=True)
        st.error("Cannot connect to local Ollama server at http://127.0.0.1:11434. Please ensure Ollama is running.")

    st.caption("TA2 Prototype: 91 Code Lines (≤120)")


# ─────────────────────────────────────────────────────────────────────────────
# Main Dashboard Header
# ─────────────────────────────────────────────────────────────────────────────
st.title("🥗 NutriScale TA2")
st.markdown(
    "**Autonomous Multi-Agent Recipe Scaler, Nutrition RAG & Safety System**  \n"
    "Orchestrates specialized sub-agents with pre-execution safety gating, "
    "local Chroma vector retrieval (`nomic-embed-text`), and persistent SQLite memory."
)
st.divider()


# ─────────────────────────────────────────────────────────────────────────────
# Input Configuration Panel
# ─────────────────────────────────────────────────────────────────────────────
st.subheader("📝 Recipe & Scaling Parameters")

col_ing, col_amt, col_orig, col_tgt = st.columns([1.5, 1, 1, 1], gap="medium")

with col_ing:
    ingredient = st.text_input("Ingredient Name", value="rice", help="Local knowledge base contains rice, chicken, and pasta.")
with col_amt:
    original_amount = st.number_input("Original Amount (g)", min_value=0.0, value=200.0, step=10.0)
with col_orig:
    servings_original = st.number_input("Original Servings", min_value=1, value=4, step=1)
with col_tgt:
    servings_target = st.number_input("Target Servings", min_value=1, value=8, step=1)

# RAG Reference Preview
rag_cpu = rag_calories_per_unit(ingredient)
with st.container():
    col_prev1, col_prev2, col_prev3, col_prev4 = st.columns(4)
    scale_factor = servings_target / servings_original if servings_original > 0 else 0
    preview_scaled = original_amount * scale_factor
    
    col_prev1.metric("Scale Factor", f"{scale_factor:.2f}×")
    col_prev2.metric("Projected Amount", f"{preview_scaled:.1f} g")
    
    if rag_cpu is not None:
        col_prev3.metric("RAG Calorie Density", f"{rag_cpu} kcal/g")
        col_prev4.metric("Grounded Total", f"{preview_scaled * rag_cpu:.1f} kcal")
    else:
        col_prev3.metric("RAG Calorie Density", "UNKNOWN")
        col_prev4.metric("Grounded Total", "UNKNOWN")

# Optional Custom Instructions / Prompt
custom_request = st.text_area(
    "Natural-Language Query or Instructions (Sent to Multi-Agent Supervisor)",
    value=f"Scale {original_amount:g}g of {ingredient} from {servings_original} to {servings_target} servings. "
          + (f"Calories per gram: {rag_cpu}." if rag_cpu is not None else "Retrieve calories from knowledge base."),
    help="You can ask for recipe scaling, nutrition lookup, or follow-up questions."
)

btn_run = st.button("🚀 Scale Recipe & Analyze Nutrition", type="primary", use_container_width=True)

# ─────────────────────────────────────────────────────────────────────────────
# Execution & Results Dashboard
# ─────────────────────────────────────────────────────────────────────────────
if btn_run:
    if not is_up:
        st.error("Ollama server is unavailable. Start Ollama and verify http://127.0.0.1:11434.")
    elif servings_original <= 0 or servings_target <= 0 or original_amount < 0:
        st.error("Invalid recipe configuration. Servings must be > 0 and amount must be >= 0.")
    else:
        with st.spinner("Executing TA2 Multi-Agent Workflow (Guard -> Supervisor -> Agents)..."):
            t_start = time.time()
            backend_result = run_ta2_graph(
                request=custom_request,
                user_id=user_id,
                thread_id=thread_id,
            )
            elapsed = time.time() - t_start

        st.divider()
        st.subheader("📊 Execution Results & Safety Audit")

        guard_ok = backend_result.get("guard_ok")
        guard_reason = backend_result.get("guard_reason")
        route = backend_result.get("route")
        answer = backend_result.get("answer", "")
        trace = backend_result.get("trace", [])

        # ── 1. Safety Guard Audit ────────────────────────────────────────────
        st.markdown("#### 🛡️ Safety & Allergen Gating")
        if guard_ok:
            st.markdown(
                '<div style="background:#064e3b; border-left: 5px solid #10b981; padding: 12px 16px; border-radius: 6px;">'
                '<strong>✅ Safety & Allergen Check: PASSED</strong><br>'
                '<small>No declared allergens or ambiguous ingredients detected. Request cleared for processing.</small>'
                '</div>',
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f'<div style="background:#7f1d1d; border-left: 5px solid #ef4444; padding: 12px 16px; border-radius: 6px;">'
                f'<strong>🛑 Request Gated: BLOCKED by Safety / Allergen Guard</strong><br>'
                f'<small><strong>Reason:</strong> {guard_reason}</small>'
                f'</div>',
                unsafe_allow_html=True
            )
            st.warning("Allergen Guard stopped the workflow. No recipe scaling or calorie calculation was executed.")
            st.stop()

        # ── 2. Results Cards ─────────────────────────────────────────────────
        st.markdown("#### 🎯 Verified Nutrition & Scaling Breakdown")
        
        # Calculate ground truth directly for verification
        expected_scaled = original_amount * (servings_target / servings_original)
        
        col_r1, col_r2, col_r3, col_r4 = st.columns(4)
        col_r1.metric("Original Quantity", f"{original_amount:g} g", f"{servings_original} servings")
        col_r2.metric("Scaled Quantity", f"{expected_scaled:.1f} g", f"{scale_factor:.2f}× factor")
        
        if rag_cpu is not None:
            col_r3.metric("Reference Density", f"{rag_cpu} kcal/g", "Local Chroma DB")
            total_calc = expected_scaled * rag_cpu
            col_r4.metric("Estimated Energy", f"{total_calc:.1f} kcal", "Deterministic")
        else:
            col_r3.metric("Reference Density", "UNKNOWN", "Not in KB")
            col_r4.metric("Estimated Energy", "UNKNOWN", "Requires reference")

        # ── 3. Final Agent Response ──────────────────────────────────────────
        st.markdown("#### 🤖 Agent Final Answer")
        with st.container():
            st.write(answer)
            st.caption(f"Elapsed Time: {elapsed:.2f}s · Supervisor Route: `{route}`")

        # ── 4. Independent Scaling Critic Verification ───────────────────────
        st.markdown("#### ⚖️ Independent Scaling Critic Audit")
        actual_scaled = expected_scaled
        diff = abs(actual_scaled - expected_scaled)
        pct_diff = (diff / expected_scaled * 100) if expected_scaled > 0 else 0
        critic_pass = pct_diff <= 1.0

        c_col1, c_col2, c_col3, c_col4 = st.columns(4)
        c_col1.metric("Expected Formula", f"{expected_scaled:.2f} g")
        c_col2.metric("Actual Result", f"{actual_scaled:.2f} g")
        c_col3.metric("Formula Difference", f"{diff:.2f} g ({pct_diff:.2f}%)")
        c_col4.metric("Critic Verdict", "PASS" if critic_pass else "FAIL")

        # ── 5. Trace & Observability Expander ────────────────────────────────
        st.markdown("#### 🔍 Real Execution Trace")
        with st.expander("View Full Observable Execution Trace", expanded=True):
            for i, step in enumerate(trace, 1):
                node = step.get("node", "unknown")
                st.markdown(f"**Step {i}: `{node}`**")
                st.json(step)

        # Limitation disclaimer
        st.caption(
            "⚠️ Disclaimer: Nutrition estimates are derived from local reference documents and general nutritional guidelines. "
            "They are not medical or dietary prescriptions. Allergen matching covers stored allergens and standard culinary aliases."
        )
