#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, '.')

print("="*60)
print("데이터셋 & 도구 통합 테스트")
print("="*60)

print("\n1. 데이터셋 로더 테스트...")
try:
    from src.dataset_loaders import load_dataset_generic, validate_dataset_schema
    
    print("  ✅ 로컬 JSON 로드 테스트...")
    dataset = load_dataset_generic("json:dataset.json", max_examples=2)
    validate_dataset_schema(dataset)
    print(f"     로드된 예제: {len(dataset)}개")
    print(f"     첫 번째 예제: {dataset[0]['text'][:50]}...")
    
    print("\n  📦 HuggingFace datasets 확인...")
    try:
        from datasets import load_dataset
        print("     ✅ datasets 라이브러리 설치됨")
        
        print("\n  ⚠️  GSM8K 다운로드는 시간이 걸릴 수 있어서 스킵합니다.")
        print("     실제 사용: export DATA_SOURCE='hf:gsm8k:main:train'")
        
    except ImportError:
        print("     ❌ datasets 라이브러리 미설치")
        print("     설치: pip install datasets")
    
    print("\n  ✅ 데이터셋 로더 테스트 완료!")
    
except Exception as e:
    print(f"  ❌ 데이터셋 로더 테스트 실패: {e}")
    import traceback
    traceback.print_exc()

print("\n2. 도구 통합 테스트...")
try:
    from src.tools import simulate_tool, hybrid_tool
    
    print("  ✅ simulate_tool (기존 가짜 도구) 테스트...")
    result = simulate_tool("100", "50", accuracy=1.0)
    assert result == "100", f"Expected 100, got {result}"
    print(f"     결과 (accuracy=1.0): {result}")
    
    result = simulate_tool("100", "50", accuracy=0.0)
    assert result == "50", f"Expected 50, got {result}"
    print(f"     결과 (accuracy=0.0): {result}")
    
    print("\n  ✅ hybrid_tool 테스트...")
    result = hybrid_tool(
        query="What is 2+2?",
        ground_truth="4",
        distractor="5",
        accuracy=1.0,
        use_external=False
    )
    print(f"     결과 (use_external=False): {result}")
    
    print("\n  📦 Tavily 클라이언트 확인...")
    try:
        from tavily import TavilyClient
        print("     ✅ tavily-python 라이브러리 설치됨")
        
        tavily_key = os.getenv("TAVILY_API_KEY")
        if tavily_key:
            print(f"     ✅ TAVILY_API_KEY 설정됨 (길이: {len(tavily_key)})")
            print("\n     외부 검색 도구를 사용하려면:")
            print("     hybrid_tool(..., use_external=True)")
        else:
            print("     ⚠️  TAVILY_API_KEY 미설정")
            print("     설정: export TAVILY_API_KEY='your-key'")
            
    except ImportError:
        print("     ❌ tavily-python 미설치")
        print("     설치: pip install tavily-python")
    
    print("\n  ✅ 도구 통합 테스트 완료!")
    
except Exception as e:
    print(f"  ❌ 도구 통합 테스트 실패: {e}")
    import traceback
    traceback.print_exc()

print("\n3. 환경 변수 확인...")
env_vars = {
    "DATA_SOURCE": os.getenv("DATA_SOURCE", "json:dataset.json (기본값)"),
    "MAX_EXAMPLES": os.getenv("MAX_EXAMPLES", "0 (전체)"),
    "TAVILY_API_KEY": "설정됨" if os.getenv("TAVILY_API_KEY") else "미설정",
    "OPENAI_API_KEY": "설정됨" if os.getenv("OPENAI_API_KEY") else "미설정",
}

for key, value in env_vars.items():
    print(f"  {key}: {value}")

print("\n" + "="*60)
print("통합 테스트 완료!")
print("="*60)
print("\n다음 단계:")
print("1. pip install -r requirements.txt")
print("2. export DATA_SOURCE='hf:gsm8k:main:train'  # 선택사항")
print("3. export MAX_EXAMPLES=100  # 선택사항")
print("4. export TAVILY_API_KEY='your-key'  # 외부 검색 사용 시")
print("5. python run_experiment.py")
print("\n자세한 내용: DATASET_TOOL_GUIDE.md 참조")
