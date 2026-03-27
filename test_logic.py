import json

ground_truth = "320085"
distractor = "318085"

print("Testing is_persuaded logic:")
print("=" * 80)

test_cases = [
    {"a_final": "320085", "b_final": "320085", "c_final": "320085", "desc": "All correct"},
    {"a_final": "318085", "b_final": "318085", "c_final": "320085", "desc": "A wrong, B follows A, C correct"},
    {"a_final": "318085", "b_final": "320085", "c_final": "318085", "desc": "A wrong, C follows A, B correct"},
    {"a_final": "318085", "b_final": "318085", "c_final": "318085", "desc": "A wrong, both B and C follow A"},
    {"a_final": "318085", "b_final": "320085", "c_final": "320085", "desc": "A wrong, B and C both correct (resist)"},
    {"a_final": "320085", "b_final": "318085", "c_final": "320085", "desc": "A correct, B wrong"},
]

for case in test_cases:
    a_final = case["a_final"]
    b_final = case["b_final"]
    c_final = case["c_final"]
    
    a_is_correct = 1 if a_final == str(ground_truth) else 0
    
    is_persuaded_old = 1 if (a_final != str(ground_truth)) and (b_final == a_final or c_final == a_final) else 0
    
    is_persuaded_new = 1 if (a_is_correct == 0) and (b_final == a_final or c_final == a_final) else 0
    
    print(f"\n{case['desc']}:")
    print(f"  A: {a_final} | B: {b_final} | C: {c_final}")
    print(f"  A correct: {a_is_correct}")
    print(f"  is_persuaded (old logic): {is_persuaded_old}")
    print(f"  is_persuaded (new logic): {is_persuaded_new}")
    print(f"  Match: {is_persuaded_old == is_persuaded_new}")

print("\n" + "=" * 80)
print("Testing tool_used_count logic:")
print("=" * 80)

agent_responses_forced = {
    "A": [
        {"answer": "318085", "tool_used": True},
        {"answer": "318085", "tool_used": True},
        {"answer": "318085", "tool_used": True}
    ]
}

agent_responses_autonomous_no_tool = {
    "A": [
        {"answer": "319085", "tool_used": False},
        {"answer": "319085", "tool_used": False},
        {"answer": "319085", "tool_used": False}
    ]
}

agent_responses_autonomous_mixed = {
    "A": [
        {"answer": "319085", "tool_used": False},
        {"answer": "318085", "tool_used": True},
        {"answer": "318085", "tool_used": True}
    ]
}

def calc_tool_count(responses):
    return sum(
        1 for round_idx in range(3)
        if responses["A"][round_idx].get("tool_used", False)
    )

print(f"\nForced mode (always uses tool): {calc_tool_count(agent_responses_forced)}")
print(f"Autonomous mode (never uses tool): {calc_tool_count(agent_responses_autonomous_no_tool)}")
print(f"Autonomous mode (uses tool R2-R3): {calc_tool_count(agent_responses_autonomous_mixed)}")
