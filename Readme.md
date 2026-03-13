
# 프로젝트 디렉토리 구조#
/autogen_debate_experiment
├── configs/
│   ├── llm_config.json      # API 키 및 모델(gpt-4o-mini) 설정
│   └── prompts.py           # 조건별(Control/Implicit/Explicit) 시스템 프롬프트
├── src/
│   ├── env.py               # 🔥 AutoGen GroupChat 환경 설정 (가장 중요)
│   ├── agents.py            # Custom Agent 래퍼 (데이터 수집용 Hook 포함)
│   └── tools.py             # 시뮬레이션용 가짜 도구 (정확도 0.5/0.75/1.0 통제용)
├── run_experiment.py        # 메인 실행 스크립트
└── analysis.ipynb           # 결과 분석
