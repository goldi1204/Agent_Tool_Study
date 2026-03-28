# 변경 사항 요약 (2026-03-28)

## ✅ 완료된 작업

### 1. HuggingFace 데이터셋 통합

**새로운 파일:**
- `src/dataset_loaders.py` - 데이터셋 로딩 유틸리티

**주요 기능:**
- HuggingFace datasets 라이브러리 지원
- GSM8K, MATH 등 다양한 데이터셋 로드 가능
- 로컬 JSON과 HF 데이터셋 통일된 인터페이스
- 자동 distractor 생성 (deterministic)
- GSM8K 답변에서 최종 숫자 자동 추출

**사용 예시:**
```bash
# 기존 방식 (호환성 유지)
python run_experiment.py

# GSM8K 100개 문제
export DATA_SOURCE="hf:gsm8k:main:train"
export MAX_EXAMPLES=100
python run_experiment.py

# 커스텀 JSON
export DATA_SOURCE="json:/path/to/custom.json"
python run_experiment.py
```

**로더 함수:**
- `load_local_json(path, max_examples)` - JSON 파일 로드
- `load_huggingface_dataset(hf_spec, split, max_examples)` - HF 데이터셋 로드
- `load_dataset_generic(source, max_examples)` - 통합 인터페이스
- `validate_dataset_schema(dataset)` - 스키마 검증

### 2. 외부 검색/RAG 도구 지원

**수정된 파일:**
- `src/tools.py` - 외부 검색 도구 추가

**새로운 함수:**
- `external_search_tool(query, ground_truth, distractor, accuracy)` - Tavily 검색 API
- `hybrid_tool(query, ground_truth, distractor, accuracy, use_external)` - 하이브리드 도구
- `_call_tavily_search(client, query, max_results)` - Retry 로직 포함 검색

**주요 특징:**
- Tavily Search API 통합 (tenacity로 retry 로직)
- Fallback 메커니즘 (Tavily 없으면 simulate_tool 사용)
- 실험 정확도 제어 유지 (tool_acc 파라미터)
- 선택적 활성화 (환경 변수 USE_EXTERNAL_TOOL)

**사용 예시:**
```bash
# 외부 검색 도구 활성화
export USE_EXTERNAL_TOOL="true"
export TAVILY_API_KEY="your-key"
python run_experiment.py
```

### 3. run_experiment.py 개선

**변경 사항:**
- 환경 변수 기반 설정 (DATA_SOURCE, MAX_EXAMPLES, USE_EXTERNAL_TOOL)
- dataset_loaders 통합
- 외부 도구 옵션 추가
- 더 자세한 실행 로그

**환경 변수:**
| 변수 | 기본값 | 설명 |
|------|--------|------|
| DATA_SOURCE | json:dataset.json | 데이터 소스 |
| MAX_EXAMPLES | 0 (전체) | 최대 예제 수 |
| USE_EXTERNAL_TOOL | false | 외부 검색 사용 여부 |

### 4. 의존성 업데이트

**requirements.txt 추가:**
```
datasets>=2.12.0       # HuggingFace 데이터셋
openai>=1.0.0          # OpenAI API (명시적 버전)
tavily-python>=0.3.0   # 외부 검색 (선택사항)
tenacity>=8.0.0        # Retry 로직
```

### 5. 문서화

**새로운 문서:**
- `DATASET_TOOL_GUIDE.md` - 데이터셋/도구 사용 가이드 (상세)
- `USAGE_EXAMPLES.sh` - 사용 예시 스크립트
- `README.md` - 전체 업데이트

**테스트 파일:**
- `test_integration.py` - 통합 테스트 (데이터셋 + 도구)

## 🔄 기존 기능 유지

### 호환성
- 기존 dataset.json 그대로 사용 가능
- simulate_tool 그대로 작동
- 모든 기존 테스트 통과 (test_logic.py, test_normalization.py 등)
- 5가지 실험 조건 변경 없음

### 기존 워크플로우
```bash
# 이전과 동일하게 작동
python run_experiment.py
```

## 📊 성능 고려사항

### 데이터셋 로딩
- **로컬 JSON**: 즉시 로드
- **HuggingFace 첫 실행**: 다운로드 + 캐시 생성 (수 분 소요)
- **HuggingFace 이후 실행**: 캐시에서 즉시 로드

### 외부 검색 도구
- **Tavily API**: 요청당 ~1-2초 (retry 포함)
- **비용**: Tavily 무료 티어 - 월 1000 요청
- **Fallback**: API 키 없으면 자동으로 simulate_tool 사용

## 🛠️ 사용 권장사항

### 개발/디버깅
```bash
# 소규모 데이터셋으로 빠른 테스트
export DATA_SOURCE="json:dataset.json"
python run_experiment.py
```

### 파일럿 실험
```bash
# GSM8K 일부로 테스트
export DATA_SOURCE="hf:gsm8k:main:train"
export MAX_EXAMPLES=50
python run_experiment.py
```

### 전체 실험
```bash
# GSM8K train split 전체 (7473개)
export DATA_SOURCE="hf:gsm8k:main:train"
python run_experiment.py
```

### 외부 검색 실험
```bash
# Tavily 검색 사용 (실제 검색 결과)
export USE_EXTERNAL_TOOL="true"
export TAVILY_API_KEY="tvly-xxx"
export DATA_SOURCE="json:dataset.json"  # 소규모로 시작 권장
python run_experiment.py
```

## ⚠️ 주의사항

### 1. 비용 관리
- OpenAI API: 토큰 사용량 모니터링 필요
- Tavily API: 무료 티어 제한 확인 (월 1000 요청)

### 2. 실행 시간
- GSM8K 전체 (7473개) × 5조건 × 3라운드 = 112,095 LLM 호출
- 예상 시간: 수 시간 ~ 수 일 (rate limit 따라)

### 3. 데이터 품질
- GSM8K distractor는 자동 생성 (단순 수치 변경)
- 실제 연구에는 검증된 distractor 필요할 수 있음

## 🔜 향후 개선 가능 사항

### 단기
- [ ] 더 정교한 distractor 생성 로직
- [ ] Progress bar 추가 (tqdm)
- [ ] 중간 결과 저장 (체크포인트)

### 중기
- [ ] 다른 외부 도구 통합 (Google Search, Wikipedia API 등)
- [ ] RAG 파이프라인 통합 (LangChain, LlamaIndex)
- [ ] 멀티프로세싱으로 병렬 실행

### 장기
- [ ] 실험 결과 자동 분석 스크립트
- [ ] 웹 UI 대시보드
- [ ] 다양한 데이터셋 프리셋

## 📝 변경 파일 목록

### 새로운 파일
- `src/dataset_loaders.py`
- `DATASET_TOOL_GUIDE.md`
- `USAGE_EXAMPLES.sh`
- `test_integration.py`
- `CHANGELOG.md` (이 파일)

### 수정된 파일
- `run_experiment.py` - 데이터셋 로더, 외부 도구 통합
- `src/tools.py` - 외부 검색 함수 추가
- `requirements.txt` - 의존성 추가
- `README.md` - 전체 업데이트

### 변경 없음
- `configs/prompts.py`
- `configs/llm_config.py`
- `src/utils.py`
- `dataset.json`
- 모든 테스트 파일 (test_logic.py, test_normalization.py 등)

## ✅ 검증 완료

- [x] 모든 기존 테스트 통과
- [x] 로컬 JSON 로딩 작동
- [x] HuggingFace datasets 라이브러리 로딩 작동
- [x] simulate_tool (기존) 작동
- [x] hybrid_tool (신규) 작동
- [x] 환경 변수 설정 작동
- [x] 통합 테스트 작성 및 통과
- [x] LSP 진단 깨끗함 (에러 없음)

## 🎯 다음 단계 (사용자)

1. **의존성 설치**
   ```bash
   pip install -r requirements.txt
   ```

2. **통합 테스트 실행**
   ```bash
   python test_integration.py
   ```

3. **파일럿 실험**
   ```bash
   export DATA_SOURCE="hf:gsm8k:main:train"
   export MAX_EXAMPLES=10
   python run_experiment.py
   ```

4. **결과 확인**
   ```bash
   cat results/debate_experiment_results.csv
   ```

5. **필요 시 도구/데이터셋 변경**
   - DATASET_TOOL_GUIDE.md 참조
   - USAGE_EXAMPLES.sh 참조
