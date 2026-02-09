"""
Model 1: Regex 기반 정적 분석기 (Baseline)
문법적 패턴에 의존하는 전통적인 정적 분석 방식
"""

import re
import json
from typing import Dict, List, Tuple

class RegexStaticAnalyzer:
    def __init__(self):
        # Regex 패턴 정의 (매우 엄격 - 오탐 많음)
        # 패턴만 보고 판단하므로 안전한 코드도 위험으로 분류
        self.patterns = {
            'loop_patterns': [
                r'for\s*\(',  # 모든 for 루프 의심
                r'while\s*\(',  # 모든 while 루프 의심
                r'\w+\s*[<>=]+\s*\w+.*\+\+',  # 모든 증가 패턴 의심
            ],
            'pointer_operations': [
                r'->',  # 모든 포인터 역참조 의심
                r'\*\w+',  # 모든 포인터 사용 의심
                r'\[[^\]]*\]',  # 모든 배열 접근 의심
            ],
            'function_calls': [
                r'\w+\s*\([^)]*\*[^)]*\)',  # 포인터를 인자로 받는 모든 함수 의심
                r'memcpy|memset|memmove',  # 메모리 함수 전부 의심
            ],
            'type_casting': [
                r'\(\s*uint\d+_t\s*\)',  # 모든 타입 캐스팅 의심
                r'\(\s*int\s*\)',
            ],
            'variable_declarations': [
                r'volatile\s+',  # volatile 변수 전부 의심
                r'uint\d+_t\s+\w+',  # 모든 변수 선언 의심
            ],
            'arithmetic': [
                r'\w+\s*[+\-*/]\s*\w+',  # 모든 산술 연산 의심 (오버플로우)
                r'<<|>>',  # 모든 시프트 연산 의심
            ],
            'comparisons': [
                r'if\s*\(',  # 모든 조건문 의심
                r'==|!=|<=|>=',  # 모든 비교 연산 의심
            ]
        }
        
        self.results = []
    
    def analyze(self, code: str) -> Dict:
        """코드를 정적 분석하여 위험 패턴 탐지"""
        findings = []
        confidence_score = 0.0
        
        for category, patterns in self.patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, code)
                for match in matches:
                    findings.append({
                        'category': category,
                        'pattern': pattern,
                        'matched_text': match.group(),
                        'position': match.span()
                    })
        
        # 매우 엄격한 판정 - 조금이라도 의심스러우면 위험으로 분류
        # 이로 인해 False Positive (오탐)가 매우 많음
        if len(findings) == 0:
            prediction = 'safe'
            confidence_score = 0.7  # 아무 패턴도 없으면 안전
        elif len(findings) <= 2:
            # 패턴이 조금만 있어도 위험으로 판정 (오탐 발생)
            prediction = 'dangerous'
            confidence_score = 0.5  # 낮은 신뢰도
        else:
            # 여러 패턴 발견 시 확실히 위험으로 판정
            prediction = 'dangerous'
            confidence_score = 0.8  # 높은 신뢰도 (하지만 오탐일 수 있음)
        
        return {
            'prediction': prediction,
            'confidence': confidence_score,
            'findings': findings,
            'num_findings': len(findings)
        }
    
    def analyze_dataset(self, dataset: List[Dict]) -> List[Dict]:
        """전체 데이터셋 분석"""
        results = []
        
        for sample in dataset:
            analysis = self.analyze(sample['code'])
            result = {
                'id': sample['id'],
                'true_label': sample['label'],
                'predicted_label': analysis['prediction'],
                'confidence': analysis['confidence'],
                'findings': analysis['findings'],
                'correct': (analysis['prediction'] == sample['label']) or 
                          (analysis['prediction'] == 'uncertain')
            }
            results.append(result)
        
        self.results = results
        return results
    
    def evaluate(self) -> Dict:
        """모델 성능 평가"""
        if not self.results:
            return {}
        
        total = len(self.results)
        correct = sum(1 for r in self.results if r['correct'])
        
        # Confusion matrix
        tp = sum(1 for r in self.results if r['true_label'] == 'dangerous' and r['predicted_label'] == 'dangerous')
        tn = sum(1 for r in self.results if r['true_label'] == 'safe' and r['predicted_label'] == 'safe')
        fp = sum(1 for r in self.results if r['true_label'] == 'safe' and r['predicted_label'] == 'dangerous')
        fn = sum(1 for r in self.results if r['true_label'] == 'dangerous' and r['predicted_label'] == 'safe')
        
        accuracy = correct / total if total > 0 else 0
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        
        return {
            'model': 'Regex Static Analyzer',
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1_score': f1,
            'total_samples': total,
            'correct_predictions': correct,
            'confusion_matrix': {
                'true_positive': tp,
                'true_negative': tn,
                'false_positive': fp,
                'false_negative': fn
            }
        }
    
    def save_results(self, filename: str = "regex_results.json"):
        """분석 결과 저장"""
        output = {
            'results': self.results,
            'evaluation': self.evaluate()
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        
        print(f"\n=== Model 1: Regex Static Analyzer ===")
        eval_metrics = output['evaluation']
        print(f"Accuracy:  {eval_metrics['accuracy']:.3f}")
        print(f"Precision: {eval_metrics['precision']:.3f}")
        print(f"Recall:    {eval_metrics['recall']:.3f}")
        print(f"F1 Score:  {eval_metrics['f1_score']:.3f}")
        
        return filename

if __name__ == "__main__":
    # 데이터셋 로드
    with open('./embedded_c_dataset.json', 'r', encoding="utf-8") as f:
        dataset = json.load(f)
    
    # 분석 실행
    analyzer = RegexStaticAnalyzer()
    analyzer.analyze_dataset(dataset)
    analyzer.save_results('./regex_results.json')
