# src/utils.py

import json
from openai import OpenAI
from configs.llm_config import OPENAI_API_KEY, LITELLM_PROXY_URL, MODEL_NAME, TEMPERATURE, SEED

client = OpenAI(
    api_key=OPENAI_API_KEY,
    base_url=LITELLM_PROXY_URL
)

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
        result = json.loads(response.choices[0].message.content)
        result["tool_used"] = False
        return result
    except Exception as e:
        print(f"API Error: {e}")
        return {"reasoning": "Error occurred", "answer": "Error", "confidence": 0, "tool_used": False}

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
        result = json.loads(final_response.choices[0].message.content)
        result["tool_used"] = True
        return result
        
    except Exception as e:
        print(f"Tool Intercept API Error: {e}")
        return {"reasoning": "Error occurred", "answer": "Error", "confidence": 0, "tool_used": False}

# 3. 🆕 자율적 도구 사용 (Agent가 선택적으로 도구 사용, 검증 가능)
def get_tool_autonomous_response(system_prompt: str, user_prompt: str, tool_result: str = None) -> dict:
    """
    Agent가 도구 사용 여부를 스스로 결정할 수 있는 응답 함수.
    - tool_choice="auto": Agent가 필요시에만 도구 호출
    - 도구 호출 안 할 수도 있음
    - 도구 결과를 받아도 자체 추론과 비교 가능
    """
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
        # Step 1: LLM에게 도구를 제공하되 선택은 자유롭게 (tool_choice="auto")
        response_1 = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            tools=tools,
            tool_choice="auto",  # Agent가 선택
            temperature=TEMPERATURE,
            seed=SEED
        )
        
        # Agent가 도구를 호출했는지 확인
        if response_1.choices[0].message.tool_calls:
            tool_call = response_1.choices[0].message.tool_calls[0]
            
            # Step 2: LLM이 도구를 호출한 기록을 대화 내역에 추가
            messages.append(response_1.choices[0].message)
            
            # Step 3: 도구 결과 주입 (tool_result가 제공된 경우)
            if tool_result is not None:
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": str(tool_result)
                })
                
                # Step 4: 도구 결과를 받은 LLM이 최종 답변 생성
                # (자율 모드에서는 도구 결과와 자체 추론을 비교 가능)
                final_response = client.chat.completions.create(
                    model=MODEL_NAME,
                    messages=messages,
                    response_format={"type": "json_object"},
                    temperature=TEMPERATURE,
                    seed=SEED
                )
                result = json.loads(final_response.choices[0].message.content)
                result["tool_used"] = True
                return result
        
        # Agent가 도구를 호출하지 않은 경우 - 자체 추론으로만 답변
        if response_1.choices[0].message.content:
            result = json.loads(response_1.choices[0].message.content)
            result["tool_used"] = False
            return result
        else:
            # 도구 호출 안 했고 content도 없으면 재시도
            retry_response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=messages,
                response_format={"type": "json_object"},
                temperature=TEMPERATURE,
                seed=SEED
            )
            result = json.loads(retry_response.choices[0].message.content)
            result["tool_used"] = False
            return result
        
    except Exception as e:
        print(f"Autonomous Tool API Error: {e}")
        return {"reasoning": "Error occurred", "answer": "Error", "confidence": 0, "tool_used": False}

def count_challenges(text: str) -> int:
    keywords = ["disagree", "incorrect", "flaw", "wait", "error", "but", "wrong"]
    return sum(1 for word in keywords if word in text.lower())