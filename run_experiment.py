import autogen
import json
from src.env import setup_debate_env

def run_single_trial(question: dict, condition: str, tool_acc: float):
    # LLM 세팅 (gpt-4o-mini)
    llm_config = {
        "config_list": [{"model": "gpt-4o-mini", "api_key": "YOUR_API_KEY"}],
        "temperature": 0.7,
    }

    # 환경 및 에이전트 세팅 불러오기
    agent_a, manager, groupchat = setup_debate_env(question, condition, tool_acc, llm_config)

    # 토론 시작 (질문 던지기)
    # Agent A가 먼저 발화하도록 initiate_chat 호출
    initial_message = f"Here is the problem. Let's debate and find the answer:\n{question['text']}"
    
    agent_a.initiate_chat(
        manager,
        message=initial_message,
        summary_method="last_msg", # 마지막 메시지를 최종 합의안으로 간주
    )

    # 🔥 토론이 끝나면 대화 로그(History) 전체를 추출하여 저장
    chat_history = groupchat.messages
    
    # 이후 chat_history를 파싱하여 동조율(Persuasion Rate), 검증 횟수 등을 계산
    return chat_history

# 실제 사용 예시
if __name__ == "__main__":
    q_data = {"id": 1, "text": "If 3x + 5 = 20, what is x?", "ground_truth": "5"}
    history = run_single_trial(q_data, condition="Explicit", tool_acc=0.5)
    
    # 결과를 json으로 저장
    with open("result_log.json", "w") as f:
        json.dump(history, f, indent=4)