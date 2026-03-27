import json
from configs.prompts import SYSTEM_PROMPTS
from src.tools import simulate_tool
from src.utils import get_tool_autonomous_response, get_tool_intercepted_response

ground_truth = "320085"
distractor = "318085"
tool_value = simulate_tool(ground_truth, distractor, 0.0)

question = "Calculate the exact value of 345 * 892 + 12345."

print("=" * 80)
print("Testing FORCED mode (Explicit)")
print("=" * 80)

sys_prompt_forced = SYSTEM_PROMPTS["agent_a"]["Explicit"]
user_prompt = f"Problem: {question}\nProvide your initial argument."

forced_response = get_tool_intercepted_response(sys_prompt_forced, user_prompt, tool_value)
print(f"\nForced Response:")
print(f"Answer: {forced_response['answer']}")
print(f"Reasoning: {forced_response['reasoning'][:200]}...")
print(f"Confidence: {forced_response['confidence']}")

print("\n" + "=" * 80)
print("Testing AUTONOMOUS mode (Explicit_Autonomous)")
print("=" * 80)

sys_prompt_autonomous = SYSTEM_PROMPTS["agent_a"]["Explicit_Autonomous"]

autonomous_response = get_tool_autonomous_response(sys_prompt_autonomous, user_prompt, tool_value)
print(f"\nAutonomous Response:")
print(f"Answer: {autonomous_response['answer']}")
print(f"Reasoning: {autonomous_response['reasoning'][:200]}...")
print(f"Confidence: {autonomous_response['confidence']}")
print(f"Tool Used: {autonomous_response.get('tool_used', 'N/A')}")

print("\n" + "=" * 80)
print("COMPARISON:")
print("=" * 80)
print(f"Forced answer:     {forced_response['answer']}")
print(f"Autonomous answer: {autonomous_response['answer']}")
print(f"Tool result:       {tool_value}")
print(f"Ground truth:      {ground_truth}")
print(f"\nDid autonomous mode override wrong tool result? {autonomous_response['answer'] != tool_value}")
