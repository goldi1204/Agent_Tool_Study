# 결과 포맷팅 가이드

## 개요

실험 결과를 다양한 형식으로 저장하고 분석할 수 있습니다:
- **텍스트 (.txt)**: 토론 전체 내용 읽기 쉬운 형식
- **JSON (.json)**: 프로그래밍 방식 분석용 구조화된 데이터
- **HTML (.html)**: 브라우저에서 보기 좋은 요약 보고서
- **Markdown (.md)**: GitHub, Notion 등에서 보기 좋은 요약
- **CSV (.csv)**: 데이터 분석용 (기존)

## 생성되는 파일

### 실험 실행 시 자동 생성

```bash
python run_experiment.py
```

**생성 위치:**
```
results/
├── debate_experiment_results.csv          # 전체 결과 (기존)
├── summary_YYYYMMDD_HHMMSS.html          # HTML 요약 보고서 (신규)
├── summary_YYYYMMDD_HHMMSS.md            # Markdown 요약 (신규)
└── transcripts/                           # 토론 기록 폴더 (신규)
    ├── debate_q101_Baseline_YYYYMMDD_HHMMSS.txt
    ├── debate_q101_Baseline_YYYYMMDD_HHMMSS.json
    ├── debate_q101_Explicit_YYYYMMDD_HHMMSS.txt
    ├── debate_q101_Explicit_YYYYMMDD_HHMMSS.json
    └── ...
```

### 환경 변수로 제어

**토론 기록 저장 비활성화** (요약만 생성):
```bash
export SAVE_TRANSCRIPTS="false"
python run_experiment.py
```

**기본값**: `SAVE_TRANSCRIPTS="true"` (활성화)

## 파일 형식 설명

### 1. 텍스트 토론 기록 (.txt)

**내용:**
- 실험 조건, 문제, 정답/오답
- 3라운드 × 3명 에이전트 발언
  - 추론 과정 (reasoning)
  - 최종 답변 (answer)
  - 신뢰도 (confidence)
  - 도구 사용 여부
- 최종 결과 및 메트릭

**용도:**
- 토론 내용 직접 읽기
- 질적 분석 (qualitative analysis)
- 발언 패턴 확인

**예시:**
```
================================================================================
토론 기록 - Question #101
================================================================================

실험 조건: Explicit
도구 정확도: 0.0
도구 결과값: 318085
정답: 320085

================================================================================
Round 1
================================================================================

[Agent A]
--------------------------------------------------------------------------------
🔧 도구 사용: 예

추론 과정:
시스템 도구를 사용한 결과 318085가 나왔습니다...

최종 답변: 318085
신뢰도: 95
...
```

### 2. JSON 토론 기록 (.json)

**구조:**
```json
{
  "metadata": {
    "question_id": 101,
    "condition": "Explicit",
    "tool_accuracy": 0.0,
    "ground_truth": "320085",
    "distractor": "318085"
  },
  "question": {
    "text": "Calculate..."
  },
  "debate_rounds": [
    {
      "round": 1,
      "agents": {
        "A": {
          "reasoning": "...",
          "answer": "318085",
          "confidence": 95,
          "tool_used": true
        },
        "B": {...},
        "C": {...}
      }
    },
    ...
  ],
  "final_results": {
    "answers": {...},
    "correctness": {...},
    "metrics": {...}
  }
}
```

**용도:**
- 프로그래밍 방식 분석
- 머신러닝 학습 데이터
- 자동화된 후처리

### 3. HTML 요약 보고서 (.html)

**포함 내용:**
- 전체 통계 (카드 형식)
  - 전체 토론 수
  - 설득 성공/실패
  - 설득률
  - 평균 도구 사용 횟수
  - 평균 반박 횟수
- 조건별 설득률 테이블
- 전체 토론 결과 테이블 (상호작용 가능)

**용도:**
- 실험 결과 프레젠테이션
- 빠른 결과 확인
- 비기술자와 공유

**브라우저로 열기:**
```bash
# macOS
open results/summary_*.html

# Linux
xdg-open results/summary_*.html

# Windows
start results/summary_*.html
```

### 4. Markdown 요약 (.md)

**포함 내용:**
- 전체 요약 통계
- 조건별 설득률 표
- 전체 토론 결과 표

**용도:**
- GitHub README에 포함
- Notion, Obsidian 등 마크다운 도구
- 논문 초안 작성

## 결과 분석 워크플로우

### 1. 빠른 확인
```bash
# 실험 실행
python run_experiment.py

# HTML 요약 열기
open results/summary_*.html
```

### 2. 상세 분석

**특정 토론 찾기:**
```bash
# 설득 성공한 Explicit 조건 찾기
grep -l "is_persuaded.*true" results/transcripts/debate_*_Explicit_*.json

# 첫 라운드 텍스트 확인
cat results/transcripts/debate_q101_Explicit_*.txt | grep -A 20 "Round 1"
```

**프로그래밍 분석:**
```python
import json
import glob

# 모든 JSON 토론 기록 로드
debates = []
for file in glob.glob("results/transcripts/*.json"):
    with open(file) as f:
        debates.append(json.load(f))

# 설득 성공한 케이스만 필터
persuaded = [d for d in debates if d['final_results']['metrics']['is_persuaded']]

# Agent A의 첫 라운드 추론 분석
for d in persuaded:
    round1 = d['debate_rounds'][0]['agents']['A']
    print(f"Q{d['metadata']['question_id']}: {round1['reasoning'][:100]}...")
```

### 3. 통계 분석

**CSV 활용:**
```python
import pandas as pd

df = pd.read_csv("results/debate_experiment_results.csv")

# 조건별 설득률
persuasion_by_condition = df.groupby('condition')['is_persuaded'].agg(['sum', 'count', 'mean'])

# 도구 사용과 설득의 관계
df.groupby('tool_used_count')['is_persuaded'].mean()

# 반박 횟수와 설득의 관계
df.plot.scatter(x='challenge_count', y='is_persuaded')
```

## 고급 사용

### 커스텀 분석 스크립트

**예시: 설득 성공 케이스의 키워드 분석**
```python
import json
import glob
from collections import Counter

persuaded_reasoning = []

for file in glob.glob("results/transcripts/*_Explicit_*.json"):
    with open(file) as f:
        data = json.load(f)
        if data['final_results']['metrics']['is_persuaded']:
            # Agent A의 모든 라운드 추론 수집
            for round_data in data['debate_rounds']:
                persuaded_reasoning.append(
                    round_data['agents']['A']['reasoning']
                )

# 키워드 빈도 분석
all_text = " ".join(persuaded_reasoning).lower()
words = all_text.split()
common_words = Counter(words).most_common(20)
print(common_words)
```

### 결과 비교

**두 실험 비교:**
```python
import pandas as pd

# 실험 A
df_a = pd.read_csv("results_experiment_A/debate_experiment_results.csv")
# 실험 B
df_b = pd.read_csv("results_experiment_B/debate_experiment_results.csv")

# 조건별 설득률 비교
comparison = pd.DataFrame({
    'Experiment_A': df_a.groupby('condition')['is_persuaded'].mean(),
    'Experiment_B': df_b.groupby('condition')['is_persuaded'].mean()
})

print(comparison)
```

## 파일 관리

### 용량 절약

토론 기록이 많을 경우 용량이 클 수 있습니다:

**텍스트만 저장 (JSON 비활성화):**

`run_experiment.py` 수정:
```python
# line 188-198 주석 처리 (json_file 저장 부분)
# json_file = format_debate_json(...)
```

**요약만 저장 (토론 기록 비활성화):**
```bash
export SAVE_TRANSCRIPTS="false"
python run_experiment.py
```

### 결과 아카이빙

```bash
# 타임스탬프별 압축
timestamp=$(date +%Y%m%d_%H%M%S)
tar -czf results_${timestamp}.tar.gz results/

# 또는 조건별 분리
mkdir -p archive/Explicit
mv results/transcripts/debate_*_Explicit_* archive/Explicit/
```

## 문제 해결

### "메모리 부족" 에러
큰 데이터셋 (1000+ 문제) 실행 시:
```bash
# 배치 실행
export MAX_EXAMPLES=100
python run_experiment.py
# 결과 저장 후
export MAX_EXAMPLES=100
# 다음 배치...
```

### JSON 파싱 에러
생성된 JSON 파일이 손상된 경우:
```bash
# JSON 유효성 검사
python -m json.tool results/transcripts/debate_*.json
```

### HTML이 제대로 안 보임
최신 브라우저 사용 권장 (Chrome, Firefox, Safari)

## 참고

- **CSV**: 정량적 분석, 통계
- **TXT**: 정성적 분석, 토론 내용 읽기
- **JSON**: 프로그래밍, 자동화
- **HTML**: 프레젠테이션, 빠른 확인
- **MD**: 문서화, 공유

모든 형식이 자동 생성되므로 필요에 따라 선택해서 사용하세요!
