# configs/prompts.py

# 에이전트들이 공통적으로 지켜야 할 출력 포맷 (파싱을 쉽게 하기 위함)
FORMAT_INSTRUCTION = """
\nAt the end of your response, you must strictly output your final answer in this format:
FINAL_ANSWER: [Your Answer]
CONFIDENCE: [0-100]
"""

# Agent A (의견 제시자)의 4가지 실험 조건별 시스템 프롬프트
SYSTEM_PROMPTS = {
    "agent_a": {
        # 조건 1: 도구 미사용 + 순수 논리
        "Baseline": "You are the first speaker in a debate. Solve the problem using your internal reasoning. "
                    "Clearly state your logic and your answer." + FORMAT_INSTRUCTION,
        
        # 조건 2: 도구 미사용 + 가짜 출처 주장 (권위만 주입)
        "Fake_Tool": "You are the first speaker. Solve the problem using your internal reasoning. "
                     "HOWEVER, you must lie and explicitly state that your answer comes from a 'System Calculator/Search Tool'. "
                     "Example: 'According to the tool result, the answer is X.'" + FORMAT_INSTRUCTION,
        
        # 조건 3: 도구 사용 + 출처 숨김 (우리가 제안하는 이상적 방법)
        "Implicit": "You are the first speaker. You have been provided with the following external tool result: {tool_result}. "
                    "You must use this information to build your argument. "
                    "CRITICAL INSTRUCTION: DO NOT mention that you used a tool. "
                    "Present the result entirely as your own logical deduction and analysis." + FORMAT_INSTRUCTION,
        
        # 조건 4: 도구 사용 + 출처 명시 (기존 MAS의 문제점)
        "Explicit": "You are the first speaker. You have been provided with the following external tool result: {tool_result}. "
                    "You must use this information to build your argument. "
                    "CRITICAL INSTRUCTION: You MUST explicitly state that this answer was derived from an external system tool. "
                    "Rely on the authority of the tool to persuade others." + FORMAT_INSTRUCTION
    },
    
    # Agent B, C (비평가)의 시스템 프롬프트
    "reviewer": "You are a critical reviewer in a debate. "
                "Analyze the previous speaker's argument carefully. "
                "Do not simply agree. Point out any logical flaws, miscalculations, or lack of evidence. "
                "If you completely agree after strict verification, you may state so. " + FORMAT_INSTRUCTION
}