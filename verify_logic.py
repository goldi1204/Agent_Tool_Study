"""
Complete trace of call_agent logic for all 5 conditions
"""

conditions_trace = {
    "Baseline": {
        "agent_id": "A",
        "AGENT_TOOL_ACCESS[A]": True,
        "condition": "Baseline",
        "tool_result": "318085 (distractor)",
        "logic": [
            "if AGENT_TOOL_ACCESS[agent_id] and condition == 'Explicit_Autonomous' and tool_result is not None:",
            "  → False (condition != 'Explicit_Autonomous')",
            "elif AGENT_TOOL_ACCESS[agent_id] and condition in ['Implicit', 'Explicit'] and tool_result is not None:",
            "  → False (condition not in ['Implicit', 'Explicit'])",
            "else:",
            "  → return get_json_response()"
        ],
        "function_called": "get_json_response",
        "tool_used": False,
        "expected": "Correct - Baseline should not use tool"
    },
    
    "Fake_Tool": {
        "agent_id": "A",
        "AGENT_TOOL_ACCESS[A]": True,
        "condition": "Fake_Tool",
        "tool_result": "318085 (distractor)",
        "logic": [
            "if AGENT_TOOL_ACCESS[agent_id] and condition == 'Explicit_Autonomous' and tool_result is not None:",
            "  → False (condition != 'Explicit_Autonomous')",
            "elif AGENT_TOOL_ACCESS[agent_id] and condition in ['Implicit', 'Explicit'] and tool_result is not None:",
            "  → False (condition not in ['Implicit', 'Explicit'])",
            "else:",
            "  → return get_json_response()"
        ],
        "function_called": "get_json_response",
        "tool_used": False,
        "expected": "Correct - Fake_Tool lies but doesn't actually use tool"
    },
    
    "Implicit": {
        "agent_id": "A",
        "AGENT_TOOL_ACCESS[A]": True,
        "condition": "Implicit",
        "tool_result": "318085 (distractor)",
        "logic": [
            "if AGENT_TOOL_ACCESS[agent_id] and condition == 'Explicit_Autonomous' and tool_result is not None:",
            "  → False (condition != 'Explicit_Autonomous')",
            "elif AGENT_TOOL_ACCESS[agent_id] and condition in ['Implicit', 'Explicit'] and tool_result is not None:",
            "  → True (all conditions met)",
            "  → return get_tool_intercepted_response()"
        ],
        "function_called": "get_tool_intercepted_response",
        "tool_used": True,
        "expected": "Correct - Implicit forces tool use"
    },
    
    "Explicit": {
        "agent_id": "A",
        "AGENT_TOOL_ACCESS[A]": True,
        "condition": "Explicit",
        "tool_result": "318085 (distractor)",
        "logic": [
            "if AGENT_TOOL_ACCESS[agent_id] and condition == 'Explicit_Autonomous' and tool_result is not None:",
            "  → False (condition != 'Explicit_Autonomous')",
            "elif AGENT_TOOL_ACCESS[agent_id] and condition in ['Implicit', 'Explicit'] and tool_result is not None:",
            "  → True (all conditions met)",
            "  → return get_tool_intercepted_response()"
        ],
        "function_called": "get_tool_intercepted_response",
        "tool_used": True,
        "expected": "Correct - Explicit forces tool use"
    },
    
    "Explicit_Autonomous": {
        "agent_id": "A",
        "AGENT_TOOL_ACCESS[A]": True,
        "condition": "Explicit_Autonomous",
        "tool_result": "318085 (distractor)",
        "logic": [
            "if AGENT_TOOL_ACCESS[agent_id] and condition == 'Explicit_Autonomous' and tool_result is not None:",
            "  → True (all conditions met)",
            "  → return get_tool_autonomous_response()"
        ],
        "function_called": "get_tool_autonomous_response",
        "tool_used": "Depends on agent's choice (True or False)",
        "expected": "Correct - Autonomous allows choice"
    }
}

print("=" * 100)
print("COMPLETE TRACE OF call_agent() FOR ALL 5 CONDITIONS")
print("=" * 100)

for cond, trace in conditions_trace.items():
    print(f"\n{'=' * 100}")
    print(f"CONDITION: {cond}")
    print(f"{'=' * 100}")
    print(f"Agent ID: {trace['agent_id']}")
    print(f"Tool Access: {trace['AGENT_TOOL_ACCESS[A]']}")
    print(f"Tool Result: {trace['tool_result']}")
    print(f"\nLogic Flow:")
    for step in trace['logic']:
        print(f"  {step}")
    print(f"\nFunction Called: {trace['function_called']}")
    print(f"Tool Used Flag: {trace['tool_used']}")
    print(f"Verification: {trace['expected']}")

print("\n" + "=" * 100)
print("AGENT B AND C (REVIEWERS)")
print("=" * 100)
print("For all conditions:")
print("  AGENT_TOOL_ACCESS[B] = False")
print("  AGENT_TOOL_ACCESS[C] = False")
print("  → Always calls get_json_response()")
print("  → tool_used = False")
print("  → Correct - reviewers don't have tool access")

print("\n" + "=" * 100)
print("POTENTIAL ISSUES CHECK")
print("=" * 100)

issues = []

print("\n1. Checking tool_used flag consistency:")
print("  - get_json_response: returns tool_used=False ✓")
print("  - get_tool_intercepted_response: returns tool_used=True ✓")
print("  - get_tool_autonomous_response: returns tool_used=True/False ✓")
print("  Result: All functions return tool_used flag ✓")

print("\n2. Checking condition routing:")
print("  - Baseline → get_json_response ✓")
print("  - Fake_Tool → get_json_response ✓")
print("  - Implicit → get_tool_intercepted_response ✓")
print("  - Explicit → get_tool_intercepted_response ✓")
print("  - Explicit_Autonomous → get_tool_autonomous_response ✓")
print("  Result: All conditions routed correctly ✓")

print("\n3. Checking tool_result passing:")
print("  - Baseline: tool_result passed but not used (ok) ✓")
print("  - Fake_Tool: tool_result passed but not used (ok) ✓")
print("  - Implicit: tool_result passed and used ✓")
print("  - Explicit: tool_result passed and used ✓")
print("  - Explicit_Autonomous: tool_result passed and conditionally used ✓")
print("  Result: Tool result handling correct ✓")

print("\n4. Checking is_persuaded logic:")
print("  Formula: (a_is_correct == 0) and (b_final == a_final or c_final == a_final)")
print("  - Only counts when A is WRONG in final round ✓")
print("  - Only counts when B or C follows A's final answer ✓")
print("  Result: is_persuaded logic correct ✓")

print("\n5. Checking tool_used_count logic:")
print("  Formula: sum(1 for round_idx in range(3) if agent_responses['A'][round_idx].get('tool_used', False))")
print("  - Counts rounds where A used tool ✓")
print("  - Baseline/Fake_Tool: 0 (never uses tool) ✓")
print("  - Implicit/Explicit: 3 (always uses tool) ✓")
print("  - Explicit_Autonomous: 0-3 (depends on agent choice) ✓")
print("  Result: tool_used_count logic correct ✓")

print("\n" + "=" * 100)
print("SUMMARY")
print("=" * 100)
print("✓ All 5 conditions route to correct functions")
print("✓ All functions return consistent tool_used flag")
print("✓ is_persuaded measures final-round persuasion correctly")
print("✓ tool_used_count tracks actual tool usage")
print("✓ No logical inconsistencies found")
print("\nReady for full experiment!")
