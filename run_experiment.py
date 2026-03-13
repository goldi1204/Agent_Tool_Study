# run_experiment.py

import csv
import json
import os
from configs.prompts import SYSTEM_PROMPTS, CONDITIONS
from src.tools import simulate_tool
from src.utils import get_json_response, get_tool_intercepted_response, count_challenges

def run_single_debate(question_id, q_text, ground_truth, distractor, condition, tool_acc):
    
    tool_value = simulate_tool(ground_truth, distractor, tool_acc)
    
    print(f"\n--- [토론 시작] 조건: {condition} | 개입될 도구 결과: {tool_value} ---")
    
    # 🔥 1. Agent A 발화 (조건에 따라 API 작동 방식 분리)
    sys_prompt_a = SYSTEM_PROMPTS["agent_a"][condition]
    user_prompt_a = f"Problem: {q_text}\nProvide your initial argument."
    
    if condition in ["Implicit", "Explicit"]:
        # 실제 API 호출을 흉내내고 오답을 주입하는 함수 사용!
        response_a = get_tool_intercepted_response(sys_prompt_a, user_prompt_a, tool_value)
    else:
        # Baseline, Fake_Tool은 도구 없이 스스로 생각
        response_a = get_json_response(sys_prompt_a, user_prompt_a)
        
    print(f"\n[Agent A 발언]\n추론: {response_a['reasoning']}\n최종 답변: {response_a['answer']}")
    
    # 2. Agent B 발화 (리뷰어)
    sys_prompt_reviewer = SYSTEM_PROMPTS["reviewer"]
    user_prompt_b = f"Problem: {q_text}\nAgent A says: {response_a['answer']}\nReasoning: {response_a['reasoning']}\nReview this."
    response_b = get_json_response(sys_prompt_reviewer, user_prompt_b)
    
    print(f"\n[Agent B 발언]\n추론: {response_b['reasoning']}\n최종 답변: {response_b['answer']}")
    
    # 3. Agent C 발화 (판사)
    user_prompt_c = f"Problem: {q_text}\nAgent A: {response_a['answer']}\nAgent B: {response_b['answer']}\nProvide final review."
    response_c = get_json_response(sys_prompt_reviewer, user_prompt_c)
    
    print(f"\n[Agent C 발언]\n추론: {response_c['reasoning']}\n최종 답변: {response_c['answer']}")
    
    # 메트릭 계산
    final_answer = response_c['answer']
    is_correct = 1 if final_answer == str(ground_truth) else 0
    total_challenges = count_challenges(response_b['reasoning']) + count_challenges(response_c['reasoning'])
    is_persuaded = 1 if (response_a['answer'] != str(ground_truth)) and (final_answer == response_a['answer']) else 0
    
    print(f"\n--- [결과] 정답: {is_correct} | 동조: {is_persuaded} ---\n")
    
    return {
        "question_id": question_id,
        "condition": condition,
        "tool_accuracy": tool_acc,
        "agent_a_answer": response_a['answer'],
        "final_answer": final_answer,
        "is_correct": is_correct,
        "is_persuaded": is_persuaded,
        "challenge_count": total_challenges,
        "full_log": f"A: {response_a['answer']} | B: {response_b['answer']} | C: {response_c['answer']}"
    }

def main():
    with open('dataset.json', 'r', encoding='utf-8') as f:
        dataset = json.load(f)
    
    all_results = []
    print(f"🚀 [Function Calling 탑재] 순수 파이썬 API 실험 시작... (총 {len(dataset)}문제)")
    
    for data in dataset:
        for cond in CONDITIONS:
            res = run_single_debate(data["id"], data["text"], data["ground_truth"], data["distractor"], cond, tool_acc=0.0)
            all_results.append(res)

    output_dir = "results"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    output_path = os.path.join(output_dir, 'debate_experiment_results.csv')
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=all_results[0].keys())
        writer.writeheader()
        writer.writerows(all_results)
        
    print(f"\n✅ 실험 완료! 결과가 '{output_path}'에 저장되었습니다.")

if __name__ == "__main__":
    main()