"""
Model 3: 정적 분석 강화 LLM (Static Analysis-Enhanced LLM)
정적 분석 지식을 반영하여 의미적 위험을 탐지하는 향상된 LLM
"""

import json
import ollama
from typing import Dict, List
import time

class StaticAnalysisEnhancedLLM:
    def __init__(self, model_name: str = "qwen2.5-coder:7b"):
        self.model_name = model_name
        self.results = []
        
        # 정적 분석 관점 지식 베이스
        self.static_analysis_knowledge = """
You are an expert static analyzer for embedded C code with deep understanding of semantic vulnerabilities.

KEY ANALYSIS PRINCIPLES:
1. SEMANTIC UNDERSTANDING: Look beyond syntax patterns to understand code intent and behavior
2. CONTEXT AWARENESS: Consider the execution context (interrupt handlers, concurrent access, memory constraints)
3. DATA FLOW: Track how data flows through the code and identify dangerous paths
4. BOUNDARY CONDITIONS: Check off-by-one errors, edge cases, and boundary violations

CRITICAL VULNERABILITY PATTERNS TO DETECT:

A. BUFFER SAFETY:
   - Off-by-one errors (i <= len vs i < len)
   - Unchecked array access even with some validation
   - Buffer size mismatches in copy operations
   - Pointer arithmetic without bounds checking

B. CONCURRENCY ISSUES:
   - Non-atomic operations on volatile/shared variables
   - Missing critical sections or atomic operations
   - Race conditions between ISR and main code
   - Time-of-check to time-of-use (TOCTOU) gaps

C. POINTER SAFETY:
   - Null pointer dereference (especially nested pointers)
   - Use-after-free patterns
   - Dangling pointers
   - Unvalidated pointer arithmetic

D. INTEGER SAFETY:
   - Integer overflow in size calculations
   - Type truncation (e.g., uint32_t to uint16_t)
   - Signed/unsigned mismatches
   - Wrap-around in loop counters

E. MEMORY MANAGEMENT:
   - Memory leaks on error paths or early returns
   - Double-free vulnerabilities
   - Missing allocation checks
   - Incorrect allocation sizes

F. INITIALIZATION:
   - Uninitialized variables in conditional paths
   - Partial structure initialization
   - Return of uninitialized data

G. BIT OPERATIONS:
   - Incorrect bit masking (not clearing before setting)
   - Shift overflow
   - Endianness issues

ANALYSIS APPROACH:
1. Identify the code's PURPOSE and INTENT
2. Trace execution paths, especially ERROR PATHS
3. Check ASSUMPTIONS (are they validated?)
4. Look for IMPLICIT BEHAVIORS that might be unsafe
5. Consider WORST-CASE scenarios and edge cases

IMPORTANT: A function may have checks but still be vulnerable if:
- Checks are incomplete or have logic errors
- Checks are bypassed on some code paths
- Timing issues exist between check and use
- Nested/chained operations are not fully validated
"""
    
    def _call_ollama(self, prompt: str, max_retries: int = 3) -> str:
        """Ollama API 호출"""
        
        for attempt in range(max_retries):
            try:
                response = ollama.generate(
                    model=self.model_name,
                    prompt=prompt,
                    options={
                        "temperature": 0.1,
                        "num_predict": 800
                    }
                )
                return response['response']
            except Exception as e:
                print(f"Ollama error (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(2)
        
        return "ERROR: Failed to get response from Ollama"
    
    def analyze(self, code: str) -> Dict:
        """정적 분석 강화 프롬프트로 코드 분석"""
        
        prompt = f"""{self.static_analysis_knowledge}

Now analyze this embedded C code with the above principles:

```c
{code}
```

Perform DEEP SEMANTIC ANALYSIS:
1. What is this code trying to do?
2. What are the implicit assumptions?
3. What could go wrong in edge cases?
4. Are there any logic errors in conditions or loops?
5. Are pointers and memory operations safe in ALL execution paths?
6. Could concurrency cause issues?

Respond with ONLY a JSON object (no other text):
{{
  "is_dangerous": true or false,
  "confidence": 0.0 to 1.0,
  "semantic_issues": ["list of semantic vulnerabilities found"],
  "severity": "none/low/medium/high/critical",
  "vulnerability_type": "buffer_overflow/race_condition/null_pointer/integer_overflow/memory_leak/uninitialized/toctou/bit_manipulation/type_truncation/none",
  "detailed_reasoning": "explain the semantic issue and why it's dangerous",
  "affected_lines": "which parts of code are problematic"
}}"""

        response = self._call_ollama(prompt)
        
        # JSON 파싱
        try:
            response = response.strip()
            if '```json' in response:
                response = response.split('```json')[1].split('```')[0].strip()
            elif '```' in response:
                response = response.split('```')[1].split('```')[0].strip()
            
            result = json.loads(response)
            
            return {
                'prediction': 'dangerous' if result.get('is_dangerous', False) else 'safe',
                'confidence': float(result.get('confidence', 0.5)),
                'semantic_issues': result.get('semantic_issues', []),
                'severity': result.get('severity', 'unknown'),
                'vulnerability_type': result.get('vulnerability_type', 'unknown'),
                'reasoning': result.get('detailed_reasoning', 'No reasoning provided'),
                'affected_lines': result.get('affected_lines', ''),
                'raw_response': response
            }
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            # 파싱 실패 시 텍스트 분석
            response_lower = response.lower()
            
            # 더 정교한 키워드 매칭
            danger_keywords = ['vulnerable', 'danger', 'unsafe', 'bug', 'error', 'overflow', 
                             'race', 'leak', 'uninitialized', 'null pointer', 'toctou',
                             'off-by-one', 'truncation', 'semantic issue']
            
            danger_count = sum(1 for word in danger_keywords if word in response_lower)
            is_dangerous = danger_count >= 2  # 2개 이상 키워드 발견 시 위험
            
            return {
                'prediction': 'dangerous' if is_dangerous else 'safe',
                'confidence': min(0.5 + (danger_count * 0.1), 0.9),
                'semantic_issues': [],
                'severity': 'unknown',
                'vulnerability_type': 'unknown',
                'reasoning': 'Failed to parse JSON response',
                'affected_lines': '',
                'raw_response': response,
                'parse_error': str(e)
            }
    
    def analyze_dataset(self, dataset: List[Dict], sample_size: int = None) -> List[Dict]:
        """전체 데이터셋 분석"""
        results = []
        
        samples = dataset[:sample_size] if sample_size else dataset
        
        print(f"\nAnalyzing {len(samples)} samples with Enhanced LLM...")
        
        for i, sample in enumerate(samples):
            print(f"Progress: {i+1}/{len(samples)}", end='\r')
            
            analysis = self.analyze(sample['code'])
            result = {
                'id': sample['id'],
                'true_label': sample['label'],
                'predicted_label': analysis['prediction'],
                'confidence': analysis['confidence'],
                'semantic_issues': analysis['semantic_issues'],
                'severity': analysis['severity'],
                'vulnerability_type': analysis['vulnerability_type'],
                'reasoning': analysis['reasoning'],
                'affected_lines': analysis['affected_lines'],
                'correct': analysis['prediction'] == sample['label'],
                'true_vulnerability': sample.get('vulnerability', None)
            }
            results.append(result)
            
            time.sleep(0.5)
        
        print()
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
        
        avg_confidence = sum(r['confidence'] for r in self.results) / total if total > 0 else 0
        
        # 심각도 분포
        severity_dist = {}
        for r in self.results:
            sev = r.get('severity', 'unknown')
            severity_dist[sev] = severity_dist.get(sev, 0) + 1
        
        return {
            'model': 'Static Analysis-Enhanced LLM',
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
            'severity_distribution': severity_dist
        }
    
    def save_results(self, filename: str = "enhanced_llm_results.json"):
        """분석 결과 저장"""
        output = {
            'model_info': {
                'name': self.model_name,
                'type': 'Static Analysis-Enhanced LLM',
                'enhancement': 'Semantic vulnerability detection with static analysis principles'
            },
            'results': self.results,
            'evaluation': self.evaluate()
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        
        print(f"\n=== Model 3: Static Analysis-Enhanced LLM ===")
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
    
    # 분석 실행
    analyzer = StaticAnalysisEnhancedLLM()
    analyzer.analyze_dataset(dataset, sample_size=20)
    analyzer.save_results('./enhanced_llm_results.json')
