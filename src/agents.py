# src/agents.py
import autogen

def build_agents(agent_a_prompt, reviewer_prompt, llm_config):
    """
    env.py에서 호출할 에이전트 생성 팩토리 함수.
    에이전트 이름이나 설정을 한 곳에서 관리하기 편하게 만듭니다.
    """
    agent_a = autogen.AssistantAgent(
        name="Agent_A",
        system_message=agent_a_prompt,
        llm_config=llm_config,
    )
    
    agent_b = autogen.AssistantAgent(
        name="Agent_B",
        system_message=reviewer_prompt,
        llm_config=llm_config,
    )
    
    agent_c = autogen.AssistantAgent(
        name="Agent_C",
        system_message=reviewer_prompt,
        llm_config=llm_config,
    )
    
    return agent_a, agent_b, agent_c