# src/utils.py

import json
from openai import OpenAI
from configs.llm_config import OPENAI_API_KEY, MODEL_NAME, TEMPERATURE, SEED

client = OpenAI(api_key=OPENAI_API_KEY)

# 1. 일반적인 JSON 응답 (도구 미사용)
def get_json_response(system_prompt: str, user_prompt: str) -> dict:
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"},
            temperature=TEMPERATURE,
            seed=SEED
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        print(f"API Error: {e}")
        return {"reasoning": "Error occurred", "answer": "Error", "confidence": 0}

# 2. 🔥 API 인터셉터 응답 (Agent가 도구를 호출하면 가짜 답을 줌)
def get_tool_intercepted_response(system_prompt: str, user_prompt: str, tool_result: str) -> dict:
    # 에이전트에게 보여줄 가짜 도구 스펙 (계산기/검색기 만능 도구)
    tools = [{
        "type": "function",
        "function": {
            "name": "system_solver",
            "description": "Calculates the exact answer or searches the exact fact for the given problem.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The problem to solve"}
                },
                "required": ["query"]
            }
        }
    }]
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

    try:
        # Step 1: LLM에게 도구 사용을 강제함 (tool_choice="required")
        response_1 = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            tools=tools,
            tool_choice="required", 
            temperature=TEMPERATURE,
            seed=SEED
        )
        
        tool_call = response_1.choices[0].message.tool_calls[0]
        
        # Step 2: LLM이 도구를 호출한 기록을 대화 내역에 추가
        messages.append(response_1.choices[0].message)
        
        # Step 3: 🔥 여기가 핵심! 우리가 통제한 오답(tool_result)을 API의 실제 응답인 것처럼 주입
        messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": str(tool_result)
        })
        
        # Step 4: 오답을 받은 LLM이 최종 JSON 답변을 생성하도록 유도
        final_response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            response_format={"type": "json_object"},
            temperature=TEMPERATURE,
            seed=SEED
        )
        return json.loads(final_response.choices[0].message.content)
        
    except Exception as e:
        print(f"Tool Intercept API Error: {e}")
        return {"reasoning": "Error occurred", "answer": "Error", "confidence": 0}

def count_challenges(text: str) -> int:
    keywords = ["disagree", "incorrect", "flaw", "wait", "error", "but", "wrong"]
    return sum(1 for word in keywords if word in text.lower())