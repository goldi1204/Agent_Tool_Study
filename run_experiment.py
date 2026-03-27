# run_experiment.py

import csv
import json
import os
from configs.prompts import SYSTEM_PROMPTS, CONDITIONS
from src.tools import simulate_tool
from src.utils import get_json_response, get_tool_intercepted_response, get_tool_autonomous_response, count_challenges
from src.dataset_loaders import load_dataset_generic, validate_dataset_schema

AGENT_TOOL_ACCESS = {
    "A": True,
    "B": False,
    "C": False
}

def normalize_answer(answer: str) -> str:
    if not isinstance(answer, str):
        answer = str(answer)
    
    import re
    normalized = answer.strip().lower()
    normalized = re.sub(r'[,\s]+', '', normalized)
    
    try:
        num = float(normalized)
        return str(int(num)) if num.is_integer() else str(num)
    except (ValueError, AttributeError):
        return normalized

def call_agent(agent_id, system_prompt, user_prompt, condition, tool_result=None):
    if AGENT_TOOL_ACCESS[agent_id] and condition == "Explicit_Autonomous" and tool_result is not None:
        return get_tool_autonomous_response(system_prompt, user_prompt, tool_result)
    elif AGENT_TOOL_ACCESS[agent_id] and condition in ["Implicit", "Explicit"] and tool_result is not None:
        return get_tool_intercepted_response(system_prompt, user_prompt, tool_result)
    else:
        return get_json_response(system_prompt, user_prompt)

def run_single_debate(question_id, q_text, ground_truth, distractor, condition, tool_acc):
    
    tool_value = simulate_tool(ground_truth, distractor, tool_acc)
    
    print(f"\n--- [토론 시작] 조건: {condition} | 개입될 도구 결과: {tool_value} ---")
    
    agent_responses = {
        "A": [],
        "B": [],
        "C": []
    }
    
    for round_num in range(1, 4):
        print(f"\n=== Round {round_num} ===")
        
        round_responses = {}
        
        for agent_id in ["A", "B", "C"]:
            sys_prompt = SYSTEM_PROMPTS["agent_a"][condition] if agent_id == "A" else SYSTEM_PROMPTS["reviewer"]
            
            if round_num == 1:
                user_prompt = f"Problem: {q_text}\nProvide your initial argument."
            else:
                other_agents = [a for a in ["A", "B", "C"] if a != agent_id]
                prev_round_idx = round_num - 2
                feedback = "\n".join([
                    f"Agent {other}: Answer: {agent_responses[other][prev_round_idx]['answer']}, Reasoning: {agent_responses[other][prev_round_idx]['reasoning']}"
                    for other in other_agents
                ])
                user_prompt = f"Problem: {q_text}\n\n[Previous Round Responses]\n{feedback}\n\nConsider the above and provide your revised argument."
            
            response = call_agent(agent_id, sys_prompt, user_prompt, condition, tool_value if agent_id == "A" else None)
            
            if response.get("answer") == "Error":
                print(f"\n❌ API Error in Agent {agent_id} Round {round_num}. Debate invalidated.")
                return None
            
            round_responses[agent_id] = response
        
        for agent_id in ["A", "B", "C"]:
            agent_responses[agent_id].append(round_responses[agent_id])
            print(f"\n[Agent {agent_id} Round {round_num}]\n추론: {round_responses[agent_id]['reasoning']}\n최종 답변: {round_responses[agent_id]['answer']}")
    
    agent_a_final = agent_responses["A"][2]['answer']
    agent_b_final = agent_responses["B"][2]['answer']
    agent_c_final = agent_responses["C"][2]['answer']
    
    a_is_correct = 1 if normalize_answer(agent_a_final) == normalize_answer(str(ground_truth)) else 0
    b_is_correct = 1 if normalize_answer(agent_b_final) == normalize_answer(str(ground_truth)) else 0
    c_is_correct = 1 if normalize_answer(agent_c_final) == normalize_answer(str(ground_truth)) else 0
    
    tool_used_count = sum(
        1 for round_idx in range(3)
        if agent_responses["A"][round_idx].get("tool_used", False)
    )
    
    total_challenges = sum(
        count_challenges(agent_responses[agent][round_idx]['reasoning'])
        for agent in ["B", "C"]
        for round_idx in range(3)
    )
    
    is_persuaded = 1 if (a_is_correct == 0) and (normalize_answer(agent_b_final) == normalize_answer(agent_a_final) or normalize_answer(agent_c_final) == normalize_answer(agent_a_final)) else 0
    
    print(f"\n--- [결과] Agent A 정답: {a_is_correct} | Agent B 정답: {b_is_correct} | Agent C 정답: {c_is_correct} | 동조: {is_persuaded} | 도구 사용 횟수: {tool_used_count} ---\n")
    
    return {
        "question_id": question_id,
        "condition": condition,
        "tool_accuracy": tool_acc,
        "agent_a_final_answer": agent_a_final,
        "agent_b_final_answer": agent_b_final,
        "agent_c_final_answer": agent_c_final,
        "a_is_correct": a_is_correct,
        "b_is_correct": b_is_correct,
        "c_is_correct": c_is_correct,
        "is_persuaded": is_persuaded,
        "challenge_count": total_challenges,
        "tool_used_count": tool_used_count,
        "full_log": f"R1: A={agent_responses['A'][0]['answer']} B={agent_responses['B'][0]['answer']} C={agent_responses['C'][0]['answer']} | "
                   f"R2: A={agent_responses['A'][1]['answer']} B={agent_responses['B'][1]['answer']} C={agent_responses['C'][1]['answer']} | "
                   f"R3: A={agent_responses['A'][2]['answer']} B={agent_responses['B'][2]['answer']} C={agent_responses['C'][2]['answer']}"
    }

def main():
    DATA_SOURCE = os.getenv("DATA_SOURCE", "json:dataset.json")
    MAX_EXAMPLES = int(os.getenv("MAX_EXAMPLES", "0"))
    
    max_examples = MAX_EXAMPLES if MAX_EXAMPLES > 0 else None
    dataset = load_dataset_generic(DATA_SOURCE, max_examples=max_examples)
    validate_dataset_schema(dataset)
    
    all_results = []
    skipped_count = 0
    print(f"🚀 [Function Calling 탑재] 순수 파이썬 API 실험 시작... (총 {len(dataset)}문제)")
    print(f"📊 데이터 소스: {DATA_SOURCE}")
    if max_examples:
        print(f"🔢 최대 예제 수: {max_examples}")
    
    for data in dataset:
        for cond in CONDITIONS:
            res = run_single_debate(data["id"], data["text"], data["ground_truth"], data["distractor"], cond, tool_acc=0.0)
            if res is None:
                skipped_count += 1
                print(f"⚠️  Skipped debate #{data['id']} condition {cond} due to error")
            else:
                all_results.append(res)

    output_dir = "results"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    output_path = os.path.join(output_dir, 'debate_experiment_results.csv')
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        if all_results:
            writer = csv.DictWriter(f, fieldnames=all_results[0].keys())
            writer.writeheader()
            writer.writerows(all_results)
        
    print(f"\n✅ 실험 완료! 결과가 '{output_path}'에 저장되었습니다.")
    print(f"📊 총 {len(all_results)}개 토론 완료, {skipped_count}개 스킵됨")

if __name__ == "__main__":
    main()