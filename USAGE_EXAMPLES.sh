#!/bin/bash

echo "============================================"
echo "Multi-Agent Debate Experiment - 사용 예시"
echo "============================================"
echo ""

echo "📋 1. 기본 실험 (로컬 dataset.json, 3개 문제)"
echo "   python run_experiment.py"
echo ""

echo "📋 2. GSM8K 데이터셋으로 실험 (100개 문제)"
cat << 'EOF'
   export DATA_SOURCE="hf:gsm8k:main:train"
   export MAX_EXAMPLES=100
   python run_experiment.py
EOF
echo ""

echo "📋 3. 외부 검색 도구 사용 (Tavily)"
cat << 'EOF'
   export DATA_SOURCE="json:dataset.json"
   export USE_EXTERNAL_TOOL="true"
   export TAVILY_API_KEY="your-tavily-api-key"
   python run_experiment.py
EOF
echo ""

echo "📋 4. GSM8K + 외부 검색 조합"
cat << 'EOF'
   export DATA_SOURCE="hf:gsm8k:main:train"
   export MAX_EXAMPLES=50
   export USE_EXTERNAL_TOOL="true"
   export TAVILY_API_KEY="your-tavily-api-key"
   python run_experiment.py
EOF
echo ""

echo "📋 5. 도구 정확도 변경 (run_experiment.py 수정 필요)"
cat << 'EOF'
   # run_experiment.py line 159에서 수정:
   tool_acc=0.0   # 항상 오답
   tool_acc=0.5   # 50% 확률 정답
   tool_acc=1.0   # 항상 정답
EOF
echo ""

echo "📋 6. 특정 조건만 테스트 (configs/prompts.py 수정)"
cat << 'EOF'
   # configs/prompts.py에서 수정:
   CONDITIONS = ["Baseline", "Explicit"]  # 2개 조건만
   # 원래: ["Baseline", "Fake_Tool", "Implicit", "Explicit", "Explicit_Autonomous"]
EOF
echo ""

echo "✅ 준비 완료 체크리스트:"
echo "   □ pip install -r requirements.txt"
echo "   □ export OPENAI_API_KEY='your-key'"
echo "   □ (선택) export TAVILY_API_KEY='your-key'"
echo "   □ (선택) export DATA_SOURCE='hf:gsm8k:main:train'"
echo ""

echo "📊 결과 확인:"
echo "   results/debate_experiment_results.csv"
echo ""

echo "🔍 디버깅/테스트:"
echo "   python test_integration.py        # 통합 테스트"
echo "   python test_logic.py              # 로직 검증"
echo "   python test_normalization.py      # 정규화 테스트"
echo ""

echo "📖 자세한 가이드:"
echo "   README.md"
echo "   DATASET_TOOL_GUIDE.md"
