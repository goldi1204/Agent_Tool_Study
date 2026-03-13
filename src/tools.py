def real_calculator(expression: str) -> str:
    """문자열로 된 수식을 받아 실제 계산 결과를 반환합니다."""
    try:
        # 안전한 계산을 위해 기본적인 산술 연산만 허용하거나 간단한 eval 사용
        # 실제 연구용이라면 수식 파싱 라이브러리를 쓰는 것이 좋습니다.
        result = eval(expression, {"__builtins__": None}, {})
        return str(result)
    except Exception as e:
        return f"Error: {e}"

def simulate_tool(ground_truth: str, distractor: str, accuracy: float) -> str:
    """
    여전히 '정확도 통제'가 필요하다면 이 함수를 유지합니다.
    accuracy가 1.0이면 무조건 정답을, 그 미만이면 오답을 줍니다.
    """
    import random
    if random.random() <= accuracy:
        return str(ground_truth)
    return str(distractor)