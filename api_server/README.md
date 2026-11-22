# NutriScale TA2 — FastAPI Gateway Service

Local FastAPI REST bridge connecting the native Android application (or any HTTP client) to the **NutriScale TA2 Multi-Agent LangGraph Architecture**, persistent SQLite memory, and Chroma RAG vector database.

---

## 1. Architecture Overview

```
                      +-----------------------------+
                      |   NutriScale Android App    |
                      |  (Kotlin / Jetpack Compose) |
                      +--------------+--------------+
                                     |
                                HTTP REST
                         (e.g., http://192.168.1.X:8000)
                                     v
                      +-----------------------------+
                      |     FastAPI Gateway Server   |
                      |      (api_server/app/main)  |
                      +--------------+--------------+
                                     |
              +----------------------+----------------------+
              |                                             |
              v                                             v
  +-----------------------+                     +-----------------------+
  | Recipe Scaler Service |                     |  Assistant & Routing  |
  | (Allergen & Bounds    |                     | (LangGraph Supervisor |
  |  Gating + RAG Lookup) |                     |  Recipe & Nutri Agents|
  +-----------+-----------+                     +-----------+-----------+
              |                                             |
              +----------------------+----------------------+
                                     |
                +--------------------+--------------------+
                |                                         |
                v                                         v
   +-------------------------+               +-------------------------+
   |   ChromaDB + Nomic      |               |  SQLite Persistent      |
   | Vector RAG Knowledge    |               |  Preferences & Allergies|
   |   (`ta2/chroma_db/`)    |               |    (`ta2/memory.db`)    |
   +-------------------------+               +-------------------------+
```

---

## 2. API Endpoints

### `GET /health`
- **Purpose**: System readiness audit without mutating state or making LLM calls.
- **Response**:
```json
{
  "status": "healthy",
  "model": "qwen2.5:3b",
  "ollama_connected": true,
  "ta2_graph_initialized": true,
  "available_models": ["nomic-embed-text:latest", "qwen2.5:3b"]
}
```

### `POST /scale`
- **Purpose**: Grounded recipe scaling with allergen validation and RAG calorie estimation.
- **Request**:
```json
{
  "ingredient_name": "rice",
  "original_amount": 200.0,
  "original_servings": 4.0,
  "target_servings": 8.0,
  "user_id": "demo_user"
}
```
- **Response (Success with RAG)**:
```json
{
  "ingredient_name": "rice",
  "original_amount": 200.0,
  "original_servings": 4.0,
  "target_servings": 8.0,
  "scale_factor": 2.0,
  "scaled_amount": 400.0,
  "estimated_calories": 520.0,
  "calorie_density": 1.3,
  "is_rag_verified": true,
  "source": "rice_nutrition.txt",
  "guard_ok": true,
  "guard_reason": null
}
```

### `POST /chat`
- **Purpose**: Conversational multi-agent execution using LangGraph StateGraph.
- **Request**:
```json
{
  "message": "What are the calories in 100g of white rice?",
  "user_id": "demo_user",
  "thread_id": "thread_session_1"
}
```
- **Response**:
```json
{
  "answer": "Based on the reference nutrition information from the local knowledge base:\n- Calories in 100g of white rice: 130 kcal\n...",
  "guard_ok": true,
  "guard_reason": null,
  "route": "nutrition",
  "trace": [...]
}
```

### `GET /allergies/{user_id}`
- **Purpose**: Fetch declared persistent allergies from SQLite.

### `POST /allergies/{user_id}` and `POST /allergies`
- **Purpose**: Add declared allergen to SQLite store.
- **Request**:
```json
{
  "user_id": "demo_user",
  "allergen": "peanut"
}
```

---

## 3. How to Run the Server

### Step 1: Ensure Ollama is Running
In PowerShell:
```powershell
ollama list
```
Verify `qwen2.5:3b` and `nomic-embed-text` are available.

### Step 2: Start FastAPI Service
In PowerShell:
```powershell
cd w:\Ayoo\NutriScale\api_server
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Step 3: Find Laptop LAN IP for Android Phone
In PowerShell:
```powershell
ipconfig
```
Look for `IPv4 Address` under your active Wi-Fi adapter (e.g., `192.168.1.15`).

### Step 4: Configure Android App
1. Open the NutriScale app on your phone.
2. Tap the bottom navigation **Preferences** icon (or go to **Allergies & Preferences**).
3. Under **API Base URL**, enter:
   `http://<YOUR_LAPTOP_IP>:8000/`
   (e.g., `http://192.168.1.15:8000/`)
4. Tap **Save Base URL**. The app will immediately test the `/health` endpoint and display connected status.
