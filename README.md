# 🥗 NutriScale

**Autonomous Recipe Scaling & Nutrition Estimation Agent**

> College Agentic AI Jury Project 
> Tech Stack: Python · LangChain · Ollama · Qwen2.5:3B · Streamlit

---

## What NutriScale Does

NutriScale is an agentic AI application that accepts a **single natural-language request** and autonomously:

1. **Scales** a recipe ingredient from an original to a target serving count  
2. **Estimates** the total calories of the scaled amount

The user never manually orchestrates the two steps. The LLM agent (powered by `qwen2.5:3b` via Ollama) decides which tools to invoke, in what order, and passes the output of the first tool as input to the second — all without additional Python glue code.

---

## Project Structure

```
NutriScale/
├── app.py              ← Streamlit UI + agent setup + trace renderer
├── tools.py            ← Two @tool functions (scale_recipe, estimate_calories)
├── run_agent_demo.py   ← CLI demo — runs the agent and prints the annotated trace
├── test_tools.py       ← Unit tests for both tools (15 test cases)
├── requirements.txt    ← Python dependencies
└── README.md           ← This file
```

---

## Architecture

```
User (natural-language request)
         │
         ▼
  ┌─────────────────────────────────┐
  │   ChatOllama (qwen2.5:3b)       │  ← Local LLM, no API key
  │   temperature=0 (deterministic) │
  └────────────┬────────────────────┘
               │ decides tool calls
               ▼
  ┌─────────────────────────────────┐
  │   create_agent()  [LangGraph]   │  ← Tool-calling loop
  │   Thought → Action → Observation│
  └────────┬───────────────────────┘
           │
    ┌──────┴──────┐
    ▼             ▼
scale_recipe   estimate_calories
  (Tool 1)       (Tool 2)
    │             ▲
    └─────────────┘
      result of Tool 1 fed
      as input to Tool 2
           │
           ▼
     Final Answer (text)
```

---

## The Two Tools

### `scale_recipe(servings_original, servings_target, ingredient_amount) → str`

Scales an ingredient amount from the original serving count to a target serving count.

| Parameter | Description |
|---|---|
| `servings_original` | How many servings the recipe currently makes (must be > 0) |
| `servings_target` | How many servings you want to make (must be > 0) |
| `ingredient_amount` | Ingredient amount for the original servings (must be ≥ 0) |

**Formula:** `scaled_amount = ingredient_amount × (servings_target / servings_original)`

### `estimate_calories(ingredient_amount, calories_per_unit) → str`

Estimates the total calories for a given (scaled) ingredient amount.

| Parameter | Description |
|---|---|
| `ingredient_amount` | Amount of the ingredient (typically the scaled result, must be ≥ 0) |
| `calories_per_unit` | Calorie density per one unit of the ingredient (must be ≥ 0) |

**Formula:** `total_calories = ingredient_amount × calories_per_unit`

---

## How Autonomous Chaining Works

`create_agent()` builds a **LangGraph** state machine:

```
start → agent_node → tools_node → agent_node → ... → end
```

1. The agent (LLM) receives the user's message.
2. The LLM emits an `AIMessage` with `tool_calls` → scale_recipe is called first.
3. The tool result is returned as a `ToolMessage`.
4. The LLM reads the observation and emits another `AIMessage` with `tool_calls` → estimate_calories is called next, using the scaled amount.
5. The second tool result is returned.
6. The LLM sees no more actions needed and generates the final text answer.

**No Python code calls the tools sequentially** — the LLM orchestrates the chain.

---

## Why Two Simple Tools Instead of One Large Tool?

| Concern | Explanation |
|---|---|
| **Separation of responsibilities** | `scale_recipe` knows nothing about calories; `estimate_calories` knows nothing about servings. Each tool does one thing well. |
| **Testability** | Each tool can be unit-tested independently with no dependencies. |
| **Reusability** | `estimate_calories` can be called with any amount — not just scaled recipe amounts. |
| **Agent orchestration** | The agent provides the orchestration logic, demonstrating autonomous chaining. Merging the tools would eliminate the observable chain. |

---

## Validation Cases

| Case | Tool | Expected Outcome |
|---|---|---|
| Normal valid input | both | Returns scaled amount / kcal |
| `servings_original = 0` | scale_recipe | ERROR: division by zero |
| `servings_original < 0` | scale_recipe | ERROR: meaningless value |
| `servings_target = 0` | scale_recipe | ERROR: meaningless value |
| `servings_target < 0` | scale_recipe | ERROR: meaningless value |
| `ingredient_amount < 0` | both | ERROR: negative quantity |
| `calories_per_unit < 0` | estimate_calories | ERROR: invalid density |
| `ingredient_amount = 0` | both | Valid (0 result) |
| `calories_per_unit = 0` | estimate_calories | Valid (0 kcal) |

---

## Installation

> All dependencies are assumed to be installed. If not:

```bash
pip install -r requirements.txt
```

Ensure Ollama is running and `qwen2.5:3b` is pulled:

```bash
ollama pull qwen2.5:3b
ollama serve        # start the Ollama server (if not already running)
```

---

## How to Run

### Streamlit Web App (recommended)

```bash
streamlit run app.py
```

### CLI Agent Demo (annotated trace)

```bash
python run_agent_demo.py
```

### Unit Tests

```bash
python test_tools.py
```

---

## Example Input / Output

**User request (sent as one message):**

> "Scale 200 grams of rice from 4 servings to 8 servings, then estimate the calories if rice has 1.3 calories per gram."

**Expected autonomous trace:**

```
USER REQUEST
────────────────────────────────────────────────────────────────
Scale 200 grams of rice from 4 servings to 8 servings, then
estimate the calories if rice has 1.3 calories per gram.

AGENT DECISION — calling tool: scale_recipe
────────────────────────────────────────────────────────────────
Tool  : scale_recipe
Args  :
        servings_original = 4
        servings_target   = 8
        ingredient_amount = 200.0

TOOL RESULT — scale_recipe
────────────────────────────────────────────────────────────────
Scaled ingredient amount: 400.00 units
(original: 200.0 for 4 servings → 400.00 for 8 servings)

AGENT DECISION — calling tool: estimate_calories
────────────────────────────────────────────────────────────────
Tool  : estimate_calories
Args  :
        ingredient_amount = 400.0
        calories_per_unit = 1.3

TOOL RESULT — estimate_calories
────────────────────────────────────────────────────────────────
Estimated calories: 520.00 kcal (400.00 × 1.3 = 520.00 kcal)

FINAL ANSWER
────────────────────────────────────────────────────────────────
For 8 servings you need 400 grams of rice, which provides
approximately 520 kcal.
```

---


