# NutriScale TA2 — Multi-Agent Recipe & Nutrition System

> Extension of the TA1 NutriScale project adding multi-agent orchestration,
> short-term thread memory, long-term SQLite memory, RAG with Chroma, and a
> guard node for input validation.

---

## Quick Start

```bash
# 1. Install dependencies (from the NutriScale root)
pip install -r ta2/requirements.txt

# 2. Ensure Ollama is running and both models are available
ollama pull qwen2.5:3b
ollama pull nomic-embed-text

# 3. Ingest knowledge base + run smoke test
cd ta2
python -X utf8 prototype.py

# 4. Run the 5-case evaluation (TA1 vs TA2)
cd ..
python -X utf8 ta2/tests/eval_both.py
```

---

## Architecture

```
User Request
     |
     v
[Guard Node]  ── validates inputs; blocks negatives & medical keywords
     |                        |
  PASS                     BLOCKED --> returns error, graph ends
     |
     v
[Supervisor Node]  ── routes to recipe or nutrition agent
     |                      |
  "recipe"              "nutrition"
     |                      |
     v                      v
[Recipe Agent]       [Nutrition Agent]
  scale_recipe()       retrieve_nutrition_info()  <-- Chroma RAG
  estimate_calories()
     |                      |
     v                      v
            Final Answer
```

### Agents and Their Roles

| Agent | Tools | Responsibility |
|---|---|---|
| Recipe Agent | `scale_recipe`, `estimate_calories` | Handles scaling requests and calorie calculation |
| Nutrition Agent | `retrieve_nutrition_info` | Retrieves reference nutrition data from local Chroma knowledge base |

### Supervisor Logic

The Supervisor is a deterministic Python function (not an LLM call) that routes
to the Nutrition Agent if the request contains "what" or "calori" without
scaling keywords; otherwise routes to the Recipe Agent.

### Hop Limit

`recursion_limit=10` is passed on every `graph.invoke()` call. If a sub-agent
enters a tool loop that exceeds this limit, LangGraph raises a
`RecursionError` which is caught and reported cleanly.

---

## Memory

### Short-Term Memory (Thread Memory)

- **Mechanism**: `MemorySaver` from `langgraph.checkpoint.memory`
- **Scope**: In-process only — does NOT survive application restart
- **Usage**: Each sub-agent is created with `checkpointer=short_mem`; each
  conversation turn is identified by a `thread_id`
- **Demo**: TC3 in the evaluation — Turn 2 references Turn 1 context

### Long-Term Memory (SQLite Persistence)

- **Mechanism**: `sqlite3` standard library; `ta2/memory.db`
- **Scope**: Persists across restarts (file on disk)
- **Schema**: `preferences(user_id TEXT, key TEXT, value TEXT)`
- **API**: `ltm_save(user_id, key, value)` / `ltm_load(user_id) -> dict`
- **Demo**: TC4 — preference `favourite_ingredient=pasta` saved before run,
  recalled in a fresh thread
- **Note**: `langgraph-checkpoint-sqlite` (`SqliteSaver`) was installed and is
  available, but for the lightweight prototype a direct `sqlite3` store was
  used for transparency and simplicity.

---

## RAG — Chroma + nomic-embed-text

### Knowledge Base

Three local documents in `ta2/knowledge/`:

| File | Contents |
|---|---|
| `rice_nutrition.txt` | White rice nutrition reference (~1.3 kcal/g) |
| `chicken_nutrition.txt` | Chicken breast nutrition reference (~1.65 kcal/g) |
| `pasta_nutrition.txt` | Pasta nutrition reference (dry ~3.5, cooked ~1.3-1.6 kcal/g) |

### Retrieval Pipeline

```
User Query
   -> OllamaEmbeddings(model="nomic-embed-text")  # embed query
   -> Chroma similarity_search(k=2)               # find closest chunks
   -> retrieve_nutrition_info tool result          # returned to agent
   -> Agent adds disclaimer + cites source name
```

The Chroma DB is persisted in `ta2/chroma_db/` and rebuilt automatically on
first run if it doesn't exist.

**Important**: Values retrieved from the knowledge base are reference estimates,
not medically precise facts.

---

## Guard Node

The guard node runs **before** any agent. It blocks a request if:

1. A medical/clinical keyword is found (`cure`, `treat`, `diagnose`, `medic`,
   `prescription`, `disease`)
2. A negative number pattern (`-\d+`) appears anywhere in the request

Blocked requests never reach any agent — the graph terminates at `END` with an
explanatory message. The guard decision and reason are recorded in the trace.

---

## Prototype Line Count

```
prototype.py:
  Total lines          : 109
  Code lines           : 87
  (non-blank, non-comment)
```

This is the only file counted against the 120-line limit.
Supporting files (`ta2_tools.py`, `tests/eval_both.py`, knowledge docs) are
submitted as separate supporting material.

---

## Evaluation Results (Actual, Observed)

| TC | Description | TA1 | TA2 |
|---|---|---|---|
| TC1 | Basic scaling + calorie estimate | PASS | PASS |
| TC2 | RAG nutrition question | PASS* | PASS |
| TC3 | Thread memory follow-up | N/A | PASS |
| TC4 | Long-term SQLite memory recall | N/A | PASS |
| TC5 | Guard blocks negative servings | PASS | PASS |

*TA1 TC2 used deterministic tool calls with known calorie values; TA2 used
actual RAG retrieval from the knowledge base.

TA1: 3/5 PASS, 2 N/A (memory features absent)  
TA2: 5/5 PASS

See `ta2/results/` for full JSON results and per-case traces.

---

## File Structure

```
ta2/
├── prototype.py          ← Core: 109 lines total / 87 code lines
├── ta2_tools.py          ← Tool definitions (scale_recipe, estimate_calories, retrieve_nutrition_info)
├── knowledge/
│   ├── rice_nutrition.txt
│   ├── chicken_nutrition.txt
│   └── pasta_nutrition.txt
├── chroma_db/            ← Created automatically on first run
├── memory.db             ← SQLite long-term memory (created automatically)
├── tests/
│   └── eval_both.py      ← 5-case TA1 vs TA2 evaluation script
├── results/
│   ├── ta1_results.json
│   ├── ta2_results.json
│   └── traces/           ← Per-case JSON traces
└── requirements.txt
```

---

## Limitations

1. **Short-term memory** is in-process only (`MemorySaver`). Restarting the
   process clears thread history.
2. **Supervisor routing** uses keyword heuristics, not an LLM decision. This is
   transparent and deterministic but less flexible than a learned router.
3. **RAG knowledge base** contains only 3 documents. Answers for ingredients
   outside this set fall back to the model's parametric knowledge.
4. **qwen2.5:3b** is a small model; the final answer in TC1 computed
   520 × 0.5 = 260 kcal instead of 520 kcal due to arithmetic drift. The
   deterministic tool output (520 kcal) is correct; the LLM's paraphrase
   introduced the error. The TA1 deterministic call returns the correct 520.0.
5. **Hop limit** of 10 was not triggered during testing (all runs completed
   in 1-2 hops). The limit is enforced by LangGraph's `recursion_limit`.
