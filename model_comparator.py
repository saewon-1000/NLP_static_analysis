"""
모델 평가 및 비교 프레임워크
4가지 모델의 성능을 비교하고 시각화
"""

import json
import matplotlib.pyplot as plt
import numpy as np
from typing import Dict, List

class ModelComparator:
    def __init__(self):
        self.models_data = {}
    
    def load_results(self, model_name: str, filepath: str):
        """모델 결과 로드"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.models_data[model_name] = data
                print(f"✓ Loaded: {model_name}")
        except FileNotFoundError:
            print(f"✗ File not found: {filepath}")
    
    def compare_metrics(self) -> Dict:
        """모델 메트릭 비교"""
        comparison = {}
        
        for model_name, data in self.models_data.items():
            eval_data = data.get('evaluation', {})
            comparison[model_name] = {
                'accuracy': eval_data.get('accuracy', 0),
                'precision': eval_data.get('precision', 0),
                'recall': eval_data.get('recall', 0),
                'f1_score': eval_data.get('f1_score', 0),
                'avg_confidence': eval_data.get('avg_confidence', 0)
            }
        
        return comparison
    
    def analyze_error_patterns(self) -> Dict:
        """오류 패턴 분석"""
        error_analysis = {}
        
        for model_name, data in self.models_data.items():
            results = data.get('results', [])
            
            false_positives = [r for r in results if r['true_label'] == 'safe' and r['predicted_label'] == 'dangerous']
            false_negatives = [r for r in results if r['true_label'] == 'dangerous' and r['predicted_label'] == 'safe']
            
            error_analysis[model_name] = {
                'false_positives': len(false_positives),
                'false_negatives': len(false_negatives),
                'fp_rate': len(false_positives) / len(results) if results else 0,
                'fn_rate': len(false_negatives) / len(results) if results else 0,
                'fp_examples': [r['id'] for r in false_positives[:3]],
                'fn_examples': [r['id'] for r in false_negatives[:3]]
            }
        
        return error_analysis
    
    def generate_comparison_report(self, output_file: str = "comparison_report.json"):
        """종합 비교 리포트 생성"""
        report = {
            'metrics_comparison': self.compare_metrics(),
            'error_analysis': self.analyze_error_patterns(),
            'summary': self._generate_summary()
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n{'='*60}")
        print("MODEL COMPARISON REPORT")
        print('='*60)
        
        # 메트릭 비교 출력
        print("\nPerformance Metrics:")
        print(f"{'Model':<35} {'Acc':>6} {'Prec':>6} {'Rec':>6} {'F1':>6}")
        print('-'*60)
        
        for model_name, metrics in report['metrics_comparison'].items():
            print(f"{model_name:<35} {metrics['accuracy']:>6.3f} {metrics['precision']:>6.3f} "
                  f"{metrics['recall']:>6.3f} {metrics['f1_score']:>6.3f}")
        
        # 오류 분석 출력
        print("\nError Analysis:")
        for model_name, errors in report['error_analysis'].items():
            print(f"\n{model_name}:")
            print(f"  False Positives: {errors['false_positives']} ({errors['fp_rate']:.1%})")
            print(f"  False Negatives: {errors['false_negatives']} ({errors['fn_rate']:.1%})")
        
        # 요약
        print("\nSummary:")
        print(report['summary'])
        
        return report
    
    def _generate_summary(self) -> str:
        """분석 요약 생성"""
        comparison = self.compare_metrics()
        
        if not comparison:
            return "No models to compare"
        
        # 최고 성능 모델 찾기
        best_f1_model = max(comparison.items(), key=lambda x: x[1]['f1_score'])[0]
        best_recall_model = max(comparison.items(), key=lambda x: x[1]['recall'])[0]
        best_precision_model = max(comparison.items(), key=lambda x: x[1]['precision'])[0]
        
        summary = f"""
Hypothesis Validation:
- Best Overall Performance (F1): {best_f1_model}
- Best Recall (Detection): {best_recall_model}
- Best Precision (Accuracy): {best_precision_model}
"""
        return summary
    
    def plot_comparison(self, output_file: str = "model_comparison.png"):
        """비교 그래프 생성"""
        comparison = self.compare_metrics()
        
        if not comparison:
            print("No data to plot")
            return
        
        models = list(comparison.keys())
        metrics = ['accuracy', 'precision', 'recall', 'f1_score']
        
        x = np.arange(len(models))
        width = 0.2
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        for i, metric in enumerate(metrics):
            values = [comparison[model][metric] for model in models]
            ax.bar(x + i*width, values, width, label=metric.capitalize())
        
        ax.set_xlabel('Models')
        ax.set_ylabel('Score')
        ax.set_title('Static Analysis Models Comparison')
        ax.set_xticks(x + width * 1.5)
        ax.set_xticklabels(models, rotation=15, ha='right')
        ax.legend()
        ax.grid(axis='y', alpha=0.3)
        ax.set_ylim(0, 1.0)
        
        plt.tight_layout()
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"\nPlot saved: {output_file}")
        
        return output_file

def main():
    """메인 실행 함수"""
    print("="*60)
    print("EMBEDDED C CODE STATIC ANALYSIS - MODEL COMPARISON")
    print("="*60)
    
    comparator = ModelComparator()
    
    # 결과 로드
    comparator.load_results("Model 1: Regex", "./regex_results.json")
    comparator.load_results("Model 2: Vanilla LLM", "./vanilla_llm_results.json")
    comparator.load_results("Model 3: Enhanced LLM", "./enhanced_llm_results.json")
    comparator.load_results("Model 4: Hybrid", "./hybrid_results.json")

    # 비교 리포트 생성
    comparator.generate_comparison_report("./comparison_report.json")
    
    # 그래프 생성 (matplotlib 사용 가능 시)
    try:
        comparator.plot_comparison("./model_comparison.png")
    except Exception as e:
        print(f"Plot generation skipped: {e}")

if __name__ == "__main__":
    main()
