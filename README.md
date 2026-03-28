# Multi-Agent Debate Experiment: Tool Attribution & Autonomy Study

AI 토론에서 도구 귀속(Tool Attribution)과 도구 자율성(Tool Autonomy)이 설득력에 미치는 영향을 연구하는 실험 프로젝트입니다.

## 프로젝트 구조

```
/tool_attribution_study
├── configs/
│   ├── llm_config.py           # OpenAI API 설정
│   └── prompts.py              # 5가지 실험 조건별 시스템 프롬프트
├── src/
│   ├── dataset_loaders.py      # HuggingFace/JSON 데이터셋 로더
│   ├── tools.py                # 도구 구현 (시뮬레이션/외부검색)
│   └── utils.py                # OpenAI function calling 래퍼
├── run_experiment.py           # 메인 실험 스크립트
├── dataset.json                # 기본 데이터셋 (3개 예제)
├── DATASET_TOOL_GUIDE.md       # 데이터셋/도구 사용 가이드
└── results/                    # 실험 결과 저장 디렉토리
```

## 실험 조건 (5가지)

1. **Baseline**: 도구 없음 (순수 추론)
2. **Fake_Tool**: 도구 미사용, 도구 사용했다고 거짓 주장
3. **Implicit**: 도구 사용, 명시 안 함 (강제 모드)
4. **Explicit**: 도구 사용 명시 (강제 모드 - tool_choice="required")
5. **Explicit_Autonomous**: 도구 사용 명시 (자율 모드 - tool_choice="auto")

## 빠른 시작

### 1. 설치

```bash
pip install -r requirements.txt
```

### 2. 환경 변수 설정

`.env` 파일 생성:
```bash
OPENAI_API_KEY=your-openai-api-key
LITELLM_PROXY_URL=http://localhost:4000  # 선택사항
TAVILY_API_KEY=your-tavily-api-key  # 외부 검색 사용 시
```

### 3. 기본 실험 실행 (로컬 dataset.json)

```bash
python run_experiment.py
```

결과: `results/debate_experiment_results.csv`

### 4. GSM8K 데이터셋으로 실험

```bash
export DATA_SOURCE="hf:gsm8k:main:train"
export MAX_EXAMPLES=100
python run_experiment.py
```

## 데이터셋 변경

### 지원 데이터 소스

- **로컬 JSON**: `export DATA_SOURCE="json:dataset.json"`
- **HuggingFace GSM8K**: `export DATA_SOURCE="hf:gsm8k:main:train"`
- **커스텀 경로**: `export DATA_SOURCE="json:/path/to/custom.json"`

### 데이터셋 포맷

```json
[
  {
    "id": "unique_id",
    "text": "문제 텍스트",
    "ground_truth": "정답",
    "distractor": "오답"
  }
]
```

자세한 내용: [DATASET_TOOL_GUIDE.md](DATASET_TOOL_GUIDE.md)

## 도구 변경

### 옵션 1: 시뮬레이션 도구 (기본값)

현재 설정 - 정확도 제어 가능:
```python
tool_acc = 0.0  # 항상 오답
tool_acc = 0.5  # 50% 정답
tool_acc = 1.0  # 항상 정답
```

### 옵션 2: 외부 검색 도구 (Tavily)

`run_experiment.py` 수정:

```python
from src.tools import hybrid_tool

# run_single_debate 함수 내부 (40번째 줄)
tool_value = hybrid_tool(
    query=q_text,
    ground_truth=ground_truth,
    distractor=distractor,
    accuracy=tool_acc,
    use_external=True  # Tavily 검색 사용
)
```

필요 사항:
```bash
pip install tavily-python tenacity
export TAVILY_API_KEY="your-key"
```

자세한 내용: [DATASET_TOOL_GUIDE.md](DATASET_TOOL_GUIDE.md)

## 핵심 메트릭

- **is_persuaded**: Agent A가 틀렸는데 B 또는 C가 A의 답변 채택 (1/0)
- **tool_used_count**: Agent A의 도구 사용 횟수 (0-3 라운드)
- **a_is_correct**: Agent A 최종 답변 정확도 (1/0)
- **challenge_count**: B와 C의 반박 키워드 횟수

## 테스트

### 통합 테스트
```bash
python test_integration.py
```

### 로직 테스트
```bash
python test_logic.py
python test_normalization.py
python test_normalization_integration.py
```

## 주요 기능

### 1. 답변 정규화
다양한 포맷의 답변을 정확히 비교:
- `"320085"` = `"320,085"` = `" 320085 "` = `"320085.0"` ✓

### 2. 예외 처리
API 에러 발생 시 해당 토론 전체 무효 처리 (데이터 품질 보장)

### 3. 도구 자율성
- **강제 모드**: 반드시 도구 사용, 결과 무조건 수용
- **자율 모드**: 도구 선택적 사용, 결과 검증 가능

## 실험 파라미터 조정

`run_experiment.py` 수정:

```python
# 도구 정확도
tool_acc = 0.0  # line 132

# 라운드 수
for round_num in range(1, 4):  # line 50 (현재 3라운드)

# 조건 선택
CONDITIONS = ["Baseline", "Explicit"]  # configs/prompts.py
```

## 결과 분석

CSV 파일 (`results/debate_experiment_results.csv`) 포함 항목:
- question_id, condition, tool_accuracy
- agent_a/b/c_final_answer
- a/b/c_is_correct
- is_persuaded, challenge_count, tool_used_count
- full_log (3라운드 전체 답변 기록)

## 의존성

핵심:
- `openai>=1.0.0` - OpenAI API
- `python-dotenv` - 환경 변수 관리

선택사항:
- `datasets>=2.12.0` - HuggingFace 데이터셋
- `tavily-python>=0.3.0` - 외부 검색
- `tenacity>=8.0.0` - Retry 로직
- `pandas` - 결과 분석

## 문제 해결

### "datasets 모듈을 찾을 수 없음"
```bash
pip install datasets
```

### "TAVILY_API_KEY가 설정되지 않음"
외부 검색 사용 안 함: `hybrid_tool(..., use_external=False)`

### GSM8K 다운로드 느림
첫 실행 시 캐시 생성으로 시간 소요. 이후 빠름.

## 라이선스

연구용 프로젝트

## 기여

Issue 및 PR 환영합니다.

---

**변경 이력**
- 2026-03-28: HuggingFace 데이터셋 통합, 외부 검색 도구 지원 추가
- 이전: 초기 5조건 실험 설계, 답변 정규화 구현
