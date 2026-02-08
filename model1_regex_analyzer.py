"""
Model 1: Regex 기반 정적 분석기 (Baseline)
문법적 패턴에 의존하는 전통적인 정적 분석 방식
"""

import re
import json
from typing import Dict, List, Tuple

class RegexStaticAnalyzer:
    def __init__(self):
        # Regex 패턴 정의 (문법적 패턴 기반)
        self.patterns = {
            'buffer_overflow': [
                r'strcpy\s*\(',  # strcpy 사용
                r'strcat\s*\(',  # strcat 사용
                r'gets\s*\(',    # gets 사용
                r'sprintf\s*\(',  # sprintf 사용 (snprintf 권장)
            ],
            'pointer_issues': [
                r'\*\s*\w+\s*=.*NULL',  # NULL 포인터 할당
                r'free\s*\([^)]+\);?\s*\*',  # free 후 사용 가능성
            ],
            'integer_issues': [
                r'malloc\s*\(\s*\w+\s*\*\s*sizeof',  # 정수 오버플로우 가능성
            ],
            'race_condition': [
                r'volatile.*=',  # volatile 변수 할당 (의심)
            ],
            'uninitialized': [
                r'int\s+\w+;',  # 초기화 안 된 변수 선언
                r'uint\d+_t\s+\w+;',
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
        
        # 발견된 패턴 수에 따라 위험도 판정
        if len(findings) == 0:
            prediction = 'safe'
            confidence_score = 0.6  # 패턴이 없다고 안전한 건 아님
        elif len(findings) <= 2:
            prediction = 'uncertain'
            confidence_score = 0.5
        else:
            prediction = 'dangerous'
            confidence_score = 0.7
        
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
