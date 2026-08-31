"""
run_agent_demo.py — NutriScale CLI Demo
========================================
Runs the agent with the canonical example question and prints the full
annotated autonomous trace to the terminal.

Usage:
  python run_agent_demo.py

This script is separate from the Streamlit app so the trace can be captured
and shown to a jury without launching a browser.
"""

import json
from langchain_ollama import ChatOllama
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage

from tools import scale_recipe, estimate_calories


# ─────────────────────────────────────────────────────────────────────────────
# Build agent
# ─────────────────────────────────────────────────────────────────────────────

def build_agent():
    llm = ChatOllama(model="qwen2.5:3b", temperature=0)

    system_prompt = (
        "You are NutriScale, an autonomous nutrition assistant. "
        "When a user asks you to scale a recipe and estimate calories, you MUST:\n"
        "  1. Call scale_recipe FIRST to get the scaled ingredient amount.\n"
        "  2. Call estimate_calories SECOND using the scaled amount from step 1.\n"
        "  3. Provide a clear final answer summarising both results.\n"
        "Always use both tools in sequence. Do not skip any tool."
    )

    return create_agent(
        model=llm,
        tools=[scale_recipe, estimate_calories],
        system_prompt=system_prompt,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Trace printer
# ─────────────────────────────────────────────────────────────────────────────

DIVIDER = "─" * 65


def _safe_json(obj) -> str:
    if isinstance(obj, dict):
        return json.dumps(obj, indent=4)
    return str(obj)


def print_annotated_trace(messages: list):
    """Print the full observable agent trace, annotated for the jury."""

    print(f"\n{'═'*65}")
    print("  NutriScale — Annotated Autonomous Agent Trace")
    print(f"{'═'*65}\n")

    message_count = len(messages)

    for idx, msg in enumerate(messages):
        is_last = (idx == message_count - 1)

        if isinstance(msg, HumanMessage):
            print(f"[1] 🧑  USER REQUEST")
            print(DIVIDER)
            print(f"    {msg.content}")
            print()

        elif isinstance(msg, AIMessage):
            if msg.tool_calls:
                for tc in msg.tool_calls:
                    print(f"[→] 🤖  AGENT DECISION — calling tool: {tc['name']}")
                    print(DIVIDER)
                    print(f"    Tool  : {tc['name']}")
                    print(f"    Args  :")
                    for k, v in tc.get("args", {}).items():
                        print(f"            {k} = {v}")
                    print()

            elif msg.content:
                if is_last:
                    print(f"[✓] ✅  FINAL ANSWER")
                else:
                    print(f"[→] 🤖  AGENT NARRATION")
                print(DIVIDER)
                print(f"    {msg.content}")
                print()

        elif isinstance(msg, ToolMessage):
            tool_name = getattr(msg, "name", "tool")
            print(f"[←] 📦  TOOL RESULT — {tool_name}")
            print(DIVIDER)
            print(f"    {msg.content}")
            print()

    print(f"{'═'*65}\n")


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

DEMO_QUESTION = (
    "Scale 200 grams of rice from 4 servings to 8 servings, "
    "then estimate the calories if rice has 1.3 calories per gram."
)


def main():
    print("\nBuilding NutriScale agent (Ollama / qwen2.5:3b)…")
    agent = build_agent()

    print(f"\nSending request to agent:\n  \"{DEMO_QUESTION}\"\n")
    print("(Agent will autonomously call scale_recipe then estimate_calories)\n")

    result = agent.invoke(
        {"messages": [HumanMessage(content=DEMO_QUESTION)]}
    )

    messages = result.get("messages", [])

    # Verify both tools were called
    tool_calls_seen = []
    for msg in messages:
        if isinstance(msg, AIMessage) and msg.tool_calls:
            for tc in msg.tool_calls:
                tool_calls_seen.append(tc["name"])

    print_annotated_trace(messages)

    print("Tool call verification:")
    print(f"  scale_recipe called    : {'scale_recipe' in tool_calls_seen}")
    print(f"  estimate_calories called: {'estimate_calories' in tool_calls_seen}")
    print(f"  Call sequence          : {' → '.join(tool_calls_seen)}")
    print()

    if "scale_recipe" in tool_calls_seen and "estimate_calories" in tool_calls_seen:
        print("✅ AUTONOMOUS CHAIN VERIFIED — agent called both tools independently.")
    else:
        print("⚠️  WARNING — not all tools were called. Check the trace above.")


if __name__ == "__main__":
    main()
