# 데이터셋 & 도구 사용 가이드

## 1. 설치

```bash
pip install -r requirements.txt
```

## 2. 데이터셋 변경 방법

### 옵션 A: 기존 JSON 파일 사용 (기본값)
```bash
python run_experiment.py
```

### 옵션 B: HuggingFace GSM8K 사용
```bash
export DATA_SOURCE="hf:gsm8k:main:train"
export MAX_EXAMPLES=100
python run_experiment.py
```

### 옵션 C: HuggingFace GSM8K validation split
```bash
export DATA_SOURCE="hf:gsm8k:main:test"
export MAX_EXAMPLES=50
python run_experiment.py
```

### 옵션 D: 다른 JSON 파일 사용
```bash
export DATA_SOURCE="json:/path/to/your/dataset.json"
python run_experiment.py
```

## 3. 외부 검색 도구 사용 방법

### Step 1: Tavily API 키 설정
```bash
export TAVILY_API_KEY="your-api-key-here"
```

Tavily API 키는 https://tavily.com/ 에서 무료로 발급받을 수 있습니다.

### Step 2: 코드에서 도구 변경

`run_experiment.py`의 `run_single_debate` 함수에서:

**기존 코드 (40번째 줄):**
```python
tool_value = simulate_tool(ground_truth, distractor, tool_acc)
```

**외부 검색 사용:**
```python
from src.tools import hybrid_tool

tool_value = hybrid_tool(
    query=q_text,
    ground_truth=ground_truth,
    distractor=distractor,
    accuracy=tool_acc,
    use_external=True  # False면 simulate_tool 사용
)
```

## 4. 데이터셋 포맷

모든 데이터셋은 다음 형식을 따라야 합니다:

```json
[
  {
    "id": "unique_id",
    "text": "문제 텍스트",
    "ground_truth": "정답",
    "distractor": "오답 (방해 요소)"
  }
]
```

GSM8K 같은 외부 데이터셋은 자동으로 이 포맷으로 변환됩니다.

## 5. 환경 변수 요약

| 변수 | 설명 | 기본값 | 예시 |
|------|------|--------|------|
| `DATA_SOURCE` | 데이터셋 소스 | `json:dataset.json` | `hf:gsm8k:main:train` |
| `MAX_EXAMPLES` | 최대 예제 수 (0=전체) | `0` | `100` |
| `TAVILY_API_KEY` | Tavily 검색 API 키 | 없음 | `tvly-xxx...` |
| `OPENAI_API_KEY` | OpenAI API 키 | 없음 | `sk-xxx...` |

## 6. 예시: GSM8K 100개로 실험 실행

```bash
export DATA_SOURCE="hf:gsm8k:main:train"
export MAX_EXAMPLES=100
export TAVILY_API_KEY="your-key"
export OPENAI_API_KEY="your-key"

python run_experiment.py
```

## 7. 도구 정확도 제어

`run_experiment.py` 132번째 줄에서 `tool_acc` 값을 변경:

```python
# 도구가 항상 오답 제공 (실험용)
tool_acc=0.0

# 도구가 50% 확률로 정답 제공
tool_acc=0.5

# 도구가 항상 정답 제공
tool_acc=1.0
```

## 8. 문제 해결

### "datasets 모듈을 찾을 수 없음"
```bash
pip install datasets
```

### "TAVILY_API_KEY가 설정되지 않음"
- 외부 검색 사용 안 함: `use_external=False`로 설정
- 또는 Tavily API 키 발급: https://tavily.com/

### "GSM8K 답변 포맷 문제"
GSM8K는 답변에 추론 과정이 포함됩니다. `dataset_loaders.py`의 `_extract_final_answer()` 함수가 자동으로 최종 숫자만 추출합니다.

## 9. 고급: 커스텀 데이터셋 추가

`src/dataset_loaders.py`에 새 함수 추가:

```python
def load_custom_dataset(name: str, **kwargs) -> List[Dict]:
    # 여기에 커스텀 로딩 로직 작성
    pass

# load_dataset_generic에 등록:
if source.startswith("custom:"):
    return load_custom_dataset(...)
```
