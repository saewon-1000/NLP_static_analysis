"""
데모용 비교 분석 - Regex 모델 결과 분석
"""

import json

def analyze_regex_performance():
    """Regex 모델 성능 분석 및 한계점 도출"""
    
    # Regex 결과 로드
    with open('./regex_results.json', 'r', encoding="utf-8") as f:
        regex_data = json.load(f)
    
    with open('./embedded_c_dataset.json', 'r', encoding="utf-8") as f:
        dataset = json.load(f)
    
    print("="*70)
    print("MODEL 1: REGEX-BASED STATIC ANALYZER - 상세 분석")
    print("="*70)
    
    eval_metrics = regex_data['evaluation']
    
    print(f"\n📊 성능 메트릭:")
    print(f"  Accuracy:  {eval_metrics['accuracy']:.3f}")
    print(f"  Precision: {eval_metrics['precision']:.3f}")
    print(f"  Recall:    {eval_metrics['recall']:.3f}")
    print(f"  F1 Score:  {eval_metrics['f1_score']:.3f}")
    
    cm = eval_metrics['confusion_matrix']
    print(f"\n📈 Confusion Matrix:")
    print(f"  True Positives:  {cm['true_positive']}")
    print(f"  True Negatives:  {cm['true_negative']}")
    print(f"  False Positives: {cm['false_positive']}")
    print(f"  False Negatives: {cm['false_negative']}")
    
    # 놓친 위험 코드 분석
    results = regex_data['results']
    false_negatives = [r for r in results if r['true_label'] == 'dangerous' and r['predicted_label'] != 'dangerous']
    
    print(f"\n❌ Regex가 놓친 의미적 취약점 ({len(false_negatives)}개):")
    
    # 데이터셋에서 상세 정보 추출
    missed_vulns = {}
    for fn in false_negatives[:10]:  # 상위 10개
        sample_id = fn['id']
        sample = next((s for s in dataset if s['id'] == sample_id), None)
        if sample:
            vuln_type = sample.get('category', 'unknown')
            if vuln_type not in missed_vulns:
                missed_vulns[vuln_type] = []
            missed_vulns[vuln_type].append({
                'id': sample_id,
                'vulnerability': sample.get('vulnerability', 'N/A'),
                'severity': sample.get('severity', 'unknown')
            })
    
    for vuln_type, cases in missed_vulns.items():
        print(f"\n  [{vuln_type}]")
        for case in cases[:3]:  # 각 타입별 3개만
            print(f"    - {case['id']}: {case['vulnerability'][:80]}...")
            print(f"      심각도: {case['severity']}")
    
    print(f"\n🔍 Regex 모델의 한계점:")
    print("""
  1. Off-by-one 오류 미탐지
     - 조건문 'i <= len'과 'i < len' 구분 불가
     - 논리적 오류는 패턴 매칭으로 찾기 어려움
  
  2. 경쟁 조건 (Race Condition) 미탐지
     - volatile 변수를 찾아도 원자성 문제는 이해 못 함
     - 멀티스레드/인터럽트 컨텍스트 분석 불가
  
  3. 의미적 NULL 포인터 역참조 미탐지
     - 중첩 포인터의 각 단계별 검증 확인 불가
     - 코드 흐름과 조건 분기 이해 못 함
  
  4. TOCTOU (Time-of-Check-to-Time-of-Use) 미탐지
     - 검사와 사용 사이의 시간 간격 분석 불가
     - 코드의 시간적 동작 순서 이해 못 함
  
  5. 메모리 누수 미탐지
     - Early return 경로의 메모리 해제 누락 확인 불가
     - 제어 흐름 분석 필요
    """)
    
    print(f"\n💡 LLM 기반 접근의 필요성:")
    print("""
  Regex는 문법적 패턴만 인식하지만, 위험한 코드의 의미와 의도를
  이해하려면 다음이 필요합니다:
  
  ✓ 코드의 실행 흐름 추적 (Control Flow Analysis)
  ✓ 데이터 흐름 분석 (Data Flow Analysis)
  ✓ 조건문의 논리적 정확성 검증
  ✓ 컨텍스트 이해 (인터럽트, 멀티스레드 등)
  ✓ 경계 조건 및 엣지 케이스 분석
  
  → 이러한 의미 기반 분석은 LLM이 더 적합함
    """)
    
    print("\n" + "="*70)
    print("다음 단계: LLM 모델 실행")
    print("="*70)
    print("""
Ollama를 설치하고 다음을 실행하세요:

1. Ollama 설치: https://ollama.ai/
2. 모델 다운로드: ollama pull qwen2.5-coder:7b
3. LLM 모델 실행:
   python model2_vanilla_llm.py
   python model3_enhanced_llm.py
4. 전체 비교:
   python model_comparator.py
    """)

if __name__ == "__main__":
    analyze_regex_performance()
