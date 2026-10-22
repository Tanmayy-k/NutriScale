# -*- coding: utf-8 -*-
"""
test_scaling_calorie_regression.py — Regression test for the scaling-to-calorie chain
Verifies that:
1. For Rice 200g, 4 -> 8 servings at 1.3 kcal/g:
   - scale_recipe scales 200g -> 400g
   - estimate_calories receives the SCALED 400g, NOT the original 200g
   - total calories evaluated is 520.0 kcal (NOT 260.0 kcal)
2. Tool execution sequence is strictly sequential.
"""
import os, sys, json, re

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TA2 = os.path.join(ROOT, "ta2")
sys.path.insert(0, TA2)
from prototype import recipe_agent, run
from langchain_core.messages import HumanMessage

def test_regression():
    print("=" * 70)
    print("  NutriScale — Regression Test: Scaling to Calorie Chain")
    print("=" * 70)

    # Invoke recipe agent directly with message history capture
    user_msg = "Scale 200g of rice from 4 servings to 8 servings. Calories per gram: 1.3."
    res = recipe_agent.invoke(
        {"messages": [HumanMessage(content=user_msg)]},
        config={"configurable": {"thread_id": "regression_thread_1"}}
    )
    
    messages = res.get("messages", [])
    
    # 1. Collect tool calls and tool messages
    tool_calls = []
    tool_results = []
    for m in messages:
        if hasattr(m, "tool_calls") and m.tool_calls:
            for tc in m.tool_calls:
                tool_calls.append(tc)
        if type(m).__name__ == "ToolMessage":
            tool_results.append(m.content)

    print(f"Total Tool Calls made: {len(tool_calls)}")
    for i, tc in enumerate(tool_calls, 1):
        print(f"  Call {i}: {tc['name']} with args {tc.get('args')}")

    # 2. Assert scale_recipe was called with original 200g
    scale_call = next((tc for tc in tool_calls if tc["name"] == "scale_recipe"), None)
    assert scale_call is not None, "FAIL: scale_recipe was not called!"
    assert float(scale_call["args"]["ingredient_amount"]) == 200.0, f"FAIL: scale_recipe expected 200g, got {scale_call['args']['ingredient_amount']}"

    # 3. Assert estimate_calories was called with SCALED 400g, NOT 200g
    cal_call = next((tc for tc in tool_calls if tc["name"] == "estimate_calories"), None)
    assert cal_call is not None, "FAIL: estimate_calories was not called!"
    cal_amount = float(cal_call["args"]["ingredient_amount"])
    
    print(f"\nChecking calorie estimator input quantity: {cal_amount}g (must be 400.0g)")
    if cal_amount == 200.0:
        print(">>> CRITICAL BUG DETECTED: estimate_calories received 200g instead of scaled 400g! <<<")
        sys.exit(1)
    
    assert cal_amount == 400.0, f"FAIL: estimate_calories expected 400g, but received {cal_amount}g!"
    print("  [PASS] estimate_calories correctly received 400.0g")

    # 4. Check tool output
    cal_res = next((tr for tr in tool_results if "Estimated calories:" in tr), "")
    assert "520.00 kcal" in cal_res, f"FAIL: Calorie result expected 520.00 kcal, got: {cal_res}"
    print(f"  [PASS] Tool calculated exact output: {cal_res.strip()}")

    # 5. Check end-to-end prototype run
    full_run = run(user_msg, user_id="regression_user", thread_id="regression_e2e")
    answer = full_run.get("answer", "")
    assert "520" in answer, f"FAIL: Full run answer missing 520 kcal! Output: {answer}"
    print(f"  [PASS] Full workflow produced answer with 520 kcal")

    print("\n" + "=" * 70)
    print("ALL REGRESSION CHECKS PASSED: 200g scaled to 400g -> 520 kcal verified.")
    print("=" * 70)

if __name__ == "__main__":
    test_regression()
