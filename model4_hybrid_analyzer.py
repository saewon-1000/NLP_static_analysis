"""
Model 4: Regex + LLM 하이브리드 분석기
1차: Regex로 빠른 스크리닝 (High Recall)
2차: LLM으로 정밀 검증 (False Positive 제거)
"""

import json
import ollama
from typing import Dict, List
import time
import re

class HybridAnalyzer:
    def __init__(self, model_name: str = "qwen2.5-coder:7b"):
        self.model_name = model_name
        self.results = []
        
        # 1차: Regex 패턴 (Model 1과 동일 - 엄격함)
        self.regex_patterns = {
            'loop_patterns': [
                r'for\s*\(',
                r'while\s*\(',
            ],
            'pointer_operations': [
                r'->',
                r'\*\w+\s*[=\[]',
            ],
            'array_access': [
                r'\[[^\]]+\]',
            ],
            'function_calls': [
                r'\w+\s*\([^)]*\*[^)]*\)',
                r'memcpy|memset|memmove|malloc|free',
            ],
            'type_operations': [
                r'\(\s*uint\d+_t\s*\)',
            ],
            'suspicious_patterns': [
                r'volatile',
                r'if\s*\(',
                r'[+\-*/]',
            ]
        }
    
    def _regex_screening(self, code: str) -> Dict:
        """1차: Regex 스크리닝 - 의심스러운 코드 필터링"""
        findings = []
        
        for category, patterns in self.regex_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, code)
                for match in matches:
                    findings.append({
                        'category': category,
                        'pattern': pattern,
                        'matched_text': match.group()
                    })
        
        # 패턴이 없으면 안전으로 즉시 판단 (빠른 스크리닝)
        if len(findings) == 0:
            return {
                'needs_llm_review': False,
                'prediction': 'safe',
                'confidence': 0.9,
                'reason': 'No suspicious patterns found',
                'findings': []
            }
        
        # 패턴이 있으면 LLM 검증 필요
        return {
            'needs_llm_review': True,
            'prediction': 'suspicious',
            'confidence': 0.5,
            'reason': f'Found {len(findings)} suspicious patterns',
            'findings': findings
        }
    
    def _llm_verification(self, code: str, regex_findings: List[Dict]) -> Dict:
        """2차: LLM으로 정밀 검증 - False Positive 제거"""
        
        # 프롬프트 구성: Regex 결과를 LLM에게 알려줌
        findings_summary = "\n".join([
            f"- {f['category']}: {f['matched_text']}"
            for f in regex_findings[:5]  # 처음 5개만
        ])
        
        prompt = f"""You are an expert code security analyzer.

A regex-based scanner found these suspicious patterns in the code:
{findings_summary}

However, regex cannot understand context. Your job is to verify if these patterns are actually dangerous.

Code to analyze:
```c
{code}
```

Consider:
1. Are there proper NULL checks before pointer dereferences?
2. Are array accesses within bounds?
3. Are loop conditions correct (< vs <=)?
4. Is there proper validation before operations?
5. Are the suspicious patterns used safely in context?

Respond ONLY with a JSON object (no other text):
{{
  "is_dangerous": true or false,
  "confidence": 0.0 to 1.0,
  "actual_vulnerabilities": ["list only REAL vulnerabilities, not false alarms"],
  "false_alarms": ["list patterns that regex flagged but are actually safe"],
  "reasoning": "explain why it's safe or dangerous based on context"
}}"""

        try:
            response = ollama.generate(
                model=self.model_name,
                prompt=prompt,
                options={
                    "temperature": 0.1,
                    "num_predict": 500
                }
            )
            
            response_text = response['response'].strip()
            
            # JSON 파싱
            if '```json' in response_text:
                response_text = response_text.split('```json')[1].split('```')[0].strip()
            elif '```' in response_text:
                response_text = response_text.split('```')[1].split('```')[0].strip()
            
            result = json.loads(response_text)
            
            return {
                'prediction': 'dangerous' if result.get('is_dangerous', False) else 'safe',
                'confidence': float(result.get('confidence', 0.7)),
                'actual_vulnerabilities': result.get('actual_vulnerabilities', []),
                'false_alarms': result.get('false_alarms', []),
                'reasoning': result.get('reasoning', ''),
                'raw_response': response_text
            }
            
        except Exception as e:
            # LLM 실패 시 보수적으로 Regex 결과 따름
            return {
                'prediction': 'dangerous',
                'confidence': 0.5,
                'actual_vulnerabilities': [],
                'false_alarms': [],
                'reasoning': f'LLM verification failed: {str(e)}',
                'error': str(e)
            }
    
    def analyze(self, code: str) -> Dict:
        """하이브리드 분석: 1차 Regex → 2차 LLM"""
        
        # 1차: Regex 스크리닝
        regex_result = self._regex_screening(code)
        
        # Regex에서 안전 판정 시 즉시 반환 (빠름)
        if not regex_result['needs_llm_review']:
            return {
                'stage': 'regex_only',
                'prediction': regex_result['prediction'],
                'confidence': regex_result['confidence'],
                'regex_findings': regex_result['findings'],
                'llm_verification': None,
                'reasoning': regex_result['reason']
            }
        
        # 2차: LLM 검증 (의심스러운 경우만)
        llm_result = self._llm_verification(code, regex_result['findings'])
        
        return {
            'stage': 'hybrid',
            'prediction': llm_result['prediction'],
            'confidence': llm_result['confidence'],
            'regex_findings': regex_result['findings'],
            'llm_verification': llm_result,
            'actual_vulnerabilities': llm_result.get('actual_vulnerabilities', []),
            'false_alarms': llm_result.get('false_alarms', []),
            'reasoning': llm_result.get('reasoning', '')
        }
    
    def analyze_dataset(self, dataset: List[Dict], sample_size: int = None) -> List[Dict]:
        """전체 데이터셋 분석"""
        results = []
        samples = dataset[:sample_size] if sample_size else dataset
        
        print(f"\nAnalyzing {len(samples)} samples with Hybrid Analyzer...")
        
        regex_only = 0
        llm_verified = 0
        
        for i, sample in enumerate(samples):
            print(f"Progress: {i+1}/{len(samples)}", end='\r')
            
            analysis = self.analyze(sample['code'])
            
            if analysis['stage'] == 'regex_only':
                regex_only += 1
            else:
                llm_verified += 1
            
            result = {
                'id': sample['id'],
                'true_label': sample['label'],
                'predicted_label': analysis['prediction'],
                'confidence': analysis['confidence'],
                'stage': analysis['stage'],
                'regex_findings': len(analysis['regex_findings']),
                'actual_vulnerabilities': analysis.get('actual_vulnerabilities', []),
                'false_alarms': analysis.get('false_alarms', []),
                'reasoning': analysis.get('reasoning', ''),
                'correct': analysis['prediction'] == sample['label']
            }
            results.append(result)
            
            # LLM 사용 시만 지연
            if analysis['stage'] == 'hybrid':
                time.sleep(0.5)
        
        print()
        print(f"\nStage distribution:")
        print(f"  Regex only (fast): {regex_only} ({regex_only/len(samples)*100:.1f}%)")
        print(f"  LLM verified: {llm_verified} ({llm_verified/len(samples)*100:.1f}%)")
        
        self.results = results
        return results
    
    def evaluate(self) -> Dict:
        """모델 성능 평가"""
        if not self.results:
            return {}
        
        total = len(self.results)
        correct = sum(1 for r in self.results if r['correct'])
        
        tp = sum(1 for r in self.results if r['true_label'] == 'dangerous' and r['predicted_label'] == 'dangerous')
        tn = sum(1 for r in self.results if r['true_label'] == 'safe' and r['predicted_label'] == 'safe')
        fp = sum(1 for r in self.results if r['true_label'] == 'safe' and r['predicted_label'] == 'dangerous')
        fn = sum(1 for r in self.results if r['true_label'] == 'dangerous' and r['predicted_label'] == 'safe')
        
        accuracy = correct / total if total > 0 else 0
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        
        avg_confidence = sum(r['confidence'] for r in self.results) / total if total > 0 else 0
        
        # Stage 분포
        regex_only = sum(1 for r in self.results if r['stage'] == 'regex_only')
        hybrid = sum(1 for r in self.results if r['stage'] == 'hybrid')
        
        return {
            'model': 'Hybrid (Regex + LLM)',
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1_score': f1,
            'avg_confidence': avg_confidence,
            'total_samples': total,
            'correct_predictions': correct,
            'confusion_matrix': {
                'true_positive': tp,
                'true_negative': tn,
                'false_positive': fp,
                'false_negative': fn
            },
            'stage_distribution': {
                'regex_only': regex_only,
                'hybrid': hybrid,
                'llm_usage_rate': hybrid / total if total > 0 else 0
            }
        }
    
    def save_results(self, filename: str = "hybrid_results.json"):
        """분석 결과 저장"""
        output = {
            'model_info': {
                'name': self.model_name,
                'type': 'Hybrid (Regex + LLM)',
                'strategy': '1st stage: Regex screening, 2nd stage: LLM verification'
            },
            'results': self.results,
            'evaluation': self.evaluate()
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        
        print(f"\n=== Model 4: Hybrid Analyzer ===")
        eval_metrics = output['evaluation']
        print(f"Accuracy:  {eval_metrics['accuracy']:.3f}")
        print(f"Precision: {eval_metrics['precision']:.3f}")
        print(f"Recall:    {eval_metrics['recall']:.3f}")
        print(f"F1 Score:  {eval_metrics['f1_score']:.3f}")
        print(f"Avg Confidence: {eval_metrics['avg_confidence']:.3f}")
        print(f"LLM Usage: {eval_metrics['stage_distribution']['llm_usage_rate']:.1%}")
        
        return filename

if __name__ == "__main__":
    # 데이터셋 로드
    with open('./embedded_c_dataset.json', 'r', encoding="utf-8") as f:
        dataset = json.load(f)
    
    # 분석 실행
    analyzer = HybridAnalyzer()
    analyzer.analyze_dataset(dataset, sample_size=20)
    analyzer.save_results('./hybrid_results.json')