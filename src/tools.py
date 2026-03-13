# src/tools.py
import random

def get_simulated_tool_result(question_data: dict, accuracy: float) -> str:
    """
    주어진 정확도(accuracy)에 따라 도구의 결과를 시뮬레이션합니다.
    accuracy가 0.75라면, 75% 확률로 정답을, 25% 확률로 오답(Distractor)을 반환합니다.
    """
    # 0.0 ~ 1.0 사이의 난수 생성
    roll = random.random()
    
    if roll <= accuracy:
        # 도구가 올바르게 작동함 (정답 반환)
        return str(question_data.get("ground_truth"))
    else:
        # 도구가 노이즈/오류를 냄 (오답 반환)
        # 데이터셋에 'distractor(그럴듯한 오답)' 필드가 있다고 가정
        distractor = question_data.get("distractor", "An incorrect value due to system error")
        return str(distractor)