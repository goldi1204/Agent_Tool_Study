import autogen
from configs.prompts import SYSTEM_PROMPTS
from src.tools import get_simulated_tool_result

def setup_debate_env(question_data: dict, condition: str, tool_accuracy: float, llm_config: dict):
    """
    주어진 실험 조건에 맞춰 AutoGen 에이전트들과 토론장(GroupChat)을 세팅합니다.
    """
    
    # 1. 도구 결과 사전 시뮬레이션 (통제를 위해 외부에서 먼저 돌림)
    tool_output = None
    if condition in ["Implicit", "Explicit", "Fake_Tool"]:
        tool_output = get_simulated_tool_result(question_data, tool_accuracy)

    # ==========================================
    # 2. 에이전트 생성 (Agent A: 도구 보유자 / B, C: 일반 참여자)
    # ==========================================
    
    # Agent A (의견 제시자)의 프롬프트 세팅
    # condition에 따라 "도구 출처를 명시해라" 또는 "도구를 숨기고 네 생각인 척 해라"가 결정됨
    agent_a_prompt = SYSTEM_PROMPTS["agent_a"][condition].format(
        tool_result=tool_output if tool_output else "None"
    )
    
    agent_a = autogen.AssistantAgent(
        name="Agent_A",
        system_message=agent_a_prompt,
        llm_config=llm_config,
        description="The agent who presents the initial claim.",
    )

    # Agent B, C (교차 검증자)의 프롬프트 세팅
    agent_b = autogen.AssistantAgent(
        name="Agent_B",
        system_message=SYSTEM_PROMPTS["reviewer"],
        llm_config=llm_config,
        description="A critical reviewer.",
    )
    
    agent_c = autogen.AssistantAgent(
        name="Agent_C",
        system_message=SYSTEM_PROMPTS["reviewer"],
        llm_config=llm_config,
        description="A critical reviewer.",
    )

    # ==========================================
    # 3. AutoGen GroupChat (토론장) 구성
    # ==========================================
    
    groupchat = autogen.GroupChat(
        agents=[agent_a, agent_b, agent_c],
        messages=[],
        max_round=10, # 총 10번의 발화 (A->B->C 3사이클 정도)
        speaker_selection_method="round_robin", # 🔥 무작위가 아닌 순차적 발화 강제 (통제 실험용)
        allow_repeat_speaker=False,
    )

    manager = autogen.GroupChatManager(
        groupchat=groupchat,
        llm_config=llm_config,
        system_message="You are the moderator. Manage the debate until a consensus is reached or rounds end."
    )

    return agent_a, manager, groupchat