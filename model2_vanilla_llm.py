"""
Model 2: Vanilla LLM 분석기 (Qwen via Ollama)
기본 LLM을 사용한 코드 분석
"""

import json
import ollama
from typing import Dict, List
import time

class VanillaLLMAnalyzer:
    def __init__(self, model_name: str = "qwen2.5-coder:7b"):
        self.model_name = model_name
        self.results = []
        
    def _call_ollama(self, prompt: str, max_retries: int = 3) -> str:
        """Ollama API 호출"""
        
        for attempt in range(max_retries):
            try:
                response = ollama.generate(
                    model=self.model_name,
                    prompt=prompt,
                    options={
                        "temperature": 0.1,  # 일관성을 위해 낮은 temperature
                        "num_predict": 500
                    }
                )
                return response['response']
            except Exception as e:
                print(f"Ollama error (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(2)
        
        return "ERROR: Failed to get response from Ollama"
    
    def analyze(self, code: str) -> Dict:
        """LLM을 사용하여 코드 분석"""
        prompt = f"""Analyze the following embedded C code for potential security vulnerabilities or bugs.

Code:
```c
{code}
```

Respond with ONLY a JSON object in this exact format (no other text):
{{
  "is_dangerous": true or false,
  "confidence": 0.0 to 1.0,
  "vulnerabilities": ["list of found vulnerabilities"],
  "reasoning": "brief explanation"
}}"""

        response = self._call_ollama(prompt)
        
        # JSON 파싱 시도
        try:
            # 코드 블록 제거
            response = response.strip()
            if '```json' in response:
                response = response.split('```json')[1].split('```')[0].strip()
            elif '```' in response:
                response = response.split('```')[1].split('```')[0].strip()
            
            result = json.loads(response)
            
            return {
                'prediction': 'dangerous' if result.get('is_dangerous', False) else 'safe',
                'confidence': float(result.get('confidence', 0.5)),
                'vulnerabilities': result.get('vulnerabilities', []),
                'reasoning': result.get('reasoning', 'No reasoning provided'),
                'raw_response': response
            }
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            # 파싱 실패 시 텍스트 기반 휴리스틱
            response_lower = response.lower()
            is_dangerous = any(word in response_lower for word in 
                             ['vulnerable', 'danger', 'risk', 'unsafe', 'bug', 'error', 'overflow'])
            
            return {
                'prediction': 'dangerous' if is_dangerous else 'safe',
                'confidence': 0.5,
                'vulnerabilities': [],
                'reasoning': 'Failed to parse JSON response',
                'raw_response': response,
                'parse_error': str(e)
            }
    
    def analyze_dataset(self, dataset: List[Dict], sample_size: int = None) -> List[Dict]:
        """전체 데이터셋 분석 (옵션: 샘플링)"""
        results = []
        
        # 샘플링 (Ollama 호출이 느릴 수 있으므로)
        samples = dataset[:sample_size] if sample_size else dataset
        
        print(f"\nAnalyzing {len(samples)} samples with Vanilla LLM...")
        
        for i, sample in enumerate(samples):
            print(f"Progress: {i+1}/{len(samples)}", end='\r')
            
            analysis = self.analyze(sample['code'])
            result = {
                'id': sample['id'],
                'true_label': sample['label'],
                'predicted_label': analysis['prediction'],
                'confidence': analysis['confidence'],
                'vulnerabilities': analysis['vulnerabilities'],
                'reasoning': analysis['reasoning'],
                'correct': analysis['prediction'] == sample['label']
            }
            results.append(result)
            
            # API 부하 방지
            time.sleep(0.5)
        
        print()  # 새 줄
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
        
        # 평균 신뢰도
        avg_confidence = sum(r['confidence'] for r in self.results) / total if total > 0 else 0
        
        return {
            'model': 'Vanilla LLM (Qwen)',
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
            }
        }
    
    def save_results(self, filename: str = "vanilla_llm_results.json"):
        """분석 결과 저장"""
        output = {
            'model_info': {
                'name': self.model_name,
                'type': 'Vanilla LLM'
            },
            'results': self.results,
            'evaluation': self.evaluate()
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        
        print(f"\n=== Model 2: Vanilla LLM ===")
        eval_metrics = output['evaluation']
        print(f"Accuracy:  {eval_metrics['accuracy']:.3f}")
        print(f"Precision: {eval_metrics['precision']:.3f}")
        print(f"Recall:    {eval_metrics['recall']:.3f}")
        print(f"F1 Score:  {eval_metrics['f1_score']:.3f}")
        print(f"Avg Confidence: {eval_metrics['avg_confidence']:.3f}")
        
        return filename

if __name__ == "__main__":
    # 데이터셋 로드
    with open('./embedded_c_dataset.json', 'r', encoding="utf-8") as f:
        dataset = json.load(f)
    
    # 분석 실행 (샘플링 - 전체 실행 시 sample_size=None)
    analyzer = VanillaLLMAnalyzer()
    
    # 테스트를 위해 20개 샘플만 분석 (전체: sample_size=None)
    analyzer.analyze_dataset(dataset, sample_size=20)
    analyzer.save_results('./vanilla_llm_results.json')
