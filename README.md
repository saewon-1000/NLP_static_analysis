# 임베디드 C 코드 의미 기반 정적 분석 프로젝트
## Semantic Static Analysis for Embedded C Code

---

## 📋 프로젝트 개요

### 연구 주제
임베디드 C 코드의 의미 기반 정적 분석을 통한 취약점 탐지

### Novel Hypothesis
**Regex 기반 정적 분석은 문법적 패턴에 의존하여 의미적으로 위험한 코드의 의도를 탐지하는 데 한계가 있다. 정적 분석 관점을 반영하여 보강된 LLM은 코드의 동작 의도를 파악함으로써 이러한 한계를 보완할 수 있다.**

---

## 🎯 프로젝트 구성

### 데이터셋
- **Synthetic 임베디드 C 코드 데이터**
  - 정상 코드 50개
  - 의미적으로 위험한 코드 50개
  - 총 100개 샘플

### 3가지 모델

#### Model 1: Regex 기반 정적 분석기 (Baseline)
- 전통적인 패턴 매칭 방식
- 문법적 특징에 기반한 탐지
- **한계**: 의미적 취약점 탐지 어려움

#### Model 2: Vanilla LLM (Qwen via Ollama)
- 기본 LLM을 활용한 코드 분석
- 사전 학습된 지식 활용
- **특징**: 일반적인 코드 이해 능력

#### Model 3: Static Analysis-Enhanced LLM
- 정적 분석 도메인 지식으로 강화된 LLM
- 의미적 취약점 탐지에 특화
- **특징**: 코드 의도와 동작 흐름 이해

---

## 🚀 빠른 시작

### 1. 환경 설정

```bash
# 필수 패키지 설치
pip install ollama matplotlib numpy

# Ollama 설치 (Model 2, 3 실행 시 필요)
# https://ollama.ai/ 에서 설치

# Qwen 모델 다운로드
ollama pull qwen2.5-coder:7b
```

### 2. 전체 실행

```bash
python run_analysis.py
```

이 스크립트는 다음 순서로 실행됩니다:
1. 데이터셋 생성
2. Model 1 실행 (Regex)
3. Model 2 실행 (Vanilla LLM) - Ollama 필요
4. Model 3 실행 (Enhanced LLM) - Ollama 필요
5. 결과 비교 및 평가

### 3. 개별 실행

```bash
# 데이터셋만 생성
python dataset_generator.py

# Model 1만 실행
python model1_regex_analyzer.py

# Model 2만 실행 (Ollama 필요)
python model2_vanilla_llm.py

# Model 3만 실행 (Ollama 필요)
python model3_enhanced_llm.py

# 결과 비교
python model_comparator.py
```

---

## 📊 출력 파일

### 데이터 파일
- `embedded_c_dataset.json`: 생성된 데이터셋
- `regex_results.json`: Model 1 분석 결과
- `vanilla_llm_results.json`: Model 2 분석 결과
- `enhanced_llm_results.json`: Model 3 분석 결과

### 분석 결과
- `comparison_report.json`: 모델 성능 비교 리포트
- `model_comparison.png`: 성능 비교 그래프

---

## 🔬 데이터셋 특징

### 정상 코드 예시
- ✅ 적절한 경계 검사
- ✅ NULL 포인터 검증
- ✅ 안전한 메모리 관리
- ✅ 올바른 타입 변환

### 위험 코드 예시 (의미적 취약점)

#### 1. Off-by-one 오류
```c
// 조건문은 있지만 논리 오류
for (int i = 0; i <= len; i++) {  // 위험: i <= len
    buffer[i] = data[i];
}
```

#### 2. 경쟁 조건 (Race Condition)
```c
// 원자성 없는 공유 변수 수정
uint32_t temp = shared_counter;
temp++;
shared_counter = temp;  // ISR과 충돌 가능
```

#### 3. 중첩 포인터 역참조
```c
if (config->mode == MODE_ENABLED) {
    config->settings->baudrate = 115200;  // settings NULL 체크 없음
}
```

#### 4. 정수 오버플로우
```c
// 곱셈 오버플로우 가능
uint16_t total_size = num_sensors * sizeof(sensor_t);
sensor_array = malloc(total_size);
```

#### 5. TOCTOU (Time-of-Check to Time-of-Use)
```c
if (device_ready()) {  // Check
    delay_ms(10);
    device_write(data, len);  // Use - 사이에 상태 변경 가능
}
```

---

## 📈 평가 메트릭

각 모델은 다음 메트릭으로 평가됩니다:

- **Accuracy**: 전체 정확도
- **Precision**: 위험으로 판정한 것 중 실제 위험 비율
- **Recall**: 실제 위험 중 탐지한 비율
- **F1 Score**: Precision과 Recall의 조화 평균

### Confusion Matrix
```
                Predicted
              Safe  Dangerous
Actual Safe    TN      FP
    Dangerous  FN      TP
```

---

## 🎓 연구 가설 검증

### 검증 포인트

1. **Regex 모델의 한계**
   - 문법적 패턴만으로는 의미적 버그 탐지 어려움
   - False Negative 높을 것으로 예상

2. **Vanilla LLM의 성능**
   - 코드 의미 이해로 Regex보다 향상
   - 하지만 도메인 특화 지식 부족

3. **Enhanced LLM의 우수성**
   - 정적 분석 원칙 적용으로 의미적 취약점 탐지
   - 높은 Recall과 Precision 예상

### 예상 결과
```
Model 1 (Regex)     : Low Recall (의미적 버그 놓침)
Model 2 (Vanilla)   : Medium Performance
Model 3 (Enhanced)  : High Recall & Precision
```

---

## 🛠️ 기술 스택

- **Python 3.8+**
- **Ollama Python Library**: LLM 추론 인터페이스
- **Qwen 2.5 Coder 7B**: 코드 특화 LLM
- **Matplotlib**: 시각화
- **NumPy**: 수치 연산

---

## 📝 프로젝트 구조

```
embedded-c-static-analysis/
├── run_analysis.py              # 메인 실행 스크립트
├── dataset_generator.py         # 데이터셋 생성기
├── model1_regex_analyzer.py     # Model 1: Regex
├── model2_vanilla_llm.py        # Model 2: Vanilla LLM
├── model3_enhanced_llm.py       # Model 3: Enhanced LLM
├── model_comparator.py          # 모델 비교 도구
├── README.md                    # 이 문서
│
├── embedded_c_dataset.json      # 생성된 데이터셋
├── regex_results.json           # Model 1 결과
├── vanilla_llm_results.json     # Model 2 결과
├── enhanced_llm_results.json    # Model 3 결과
├── comparison_report.json       # 비교 리포트
└── model_comparison.png         # 비교 그래프
```

---

## 🔍 상세 분석 가이드

### Model 1 (Regex) 분석
```python
from model1_regex_analyzer import RegexStaticAnalyzer

analyzer = RegexStaticAnalyzer()
result = analyzer.analyze(your_code)
print(result['findings'])
```

### Model 2 (Vanilla LLM) 분석
```python
from model2_vanilla_llm import VanillaLLMAnalyzer

analyzer = VanillaLLMAnalyzer()
result = analyzer.analyze(your_code)
print(result['reasoning'])
```

### Model 3 (Enhanced LLM) 분석
```python
from model3_enhanced_llm import StaticAnalysisEnhancedLLM

analyzer = StaticAnalysisEnhancedLLM()
result = analyzer.analyze(your_code)
print(result['semantic_issues'])
```

---

## 🎯 사용 예시

### 새로운 코드 분석하기

```python
code_sample = """
void process_data(uint8_t *input, int len) {
    for (int i = 0; i <= len; i++) {  // 의심스러운 부분
        buffer[i] = input[i];
    }
}
"""

# Enhanced LLM으로 분석
from model3_enhanced_llm import StaticAnalysisEnhancedLLM

analyzer = StaticAnalysisEnhancedLLM()
result = analyzer.analyze(code_sample)

print(f"위험도: {result['prediction']}")
print(f"신뢰도: {result['confidence']}")
print(f"발견된 문제: {result['semantic_issues']}")
print(f"상세 설명: {result['reasoning']}")
```

---

## 📚 참고 자료

### 정적 분석 원칙
- Buffer overflow detection
- Race condition analysis
- Pointer safety verification
- Integer overflow prevention
- Memory leak detection

### 임베디드 시스템 특성
- Interrupt handling
- Concurrent access patterns
- Resource constraints
- Real-time requirements

---

## ⚠️ 주의사항

1. **Ollama 설정**
   - Model 2, 3 실행 시 Ollama가 설치되어 있어야 함
   - Python ollama 패키지 필요: `pip install ollama`
   - 모델 다운로드 필요: `ollama pull qwen2.5-coder:7b`

2. **실행 시간**
   - LLM 모델은 샘플당 1-2초 소요
   - 전체 데이터셋(100개) 분석에 3-5분 소요

3. **메모리 요구사항**
   - Qwen 7B 모델: 최소 8GB RAM 권장

---

## 🤝 기여 및 개선

### 개선 아이디어
- [ ] 더 많은 취약점 패턴 추가
- [ ] 실제 임베디드 프로젝트 코드 분석
- [ ] 다른 LLM 모델 비교 (GPT, Claude 등)
- [ ] 웹 UI 개발
- [ ] CI/CD 파이프라인 통합

---

## 📧 연락처

프로젝트 관련 문의나 제안 사항이 있으시면 이슈를 등록해주세요.

---

## 📄 라이선스

MIT License

---

**Happy Analyzing! 🚀**
