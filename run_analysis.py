#!/usr/bin/env python3
"""
메인 실행 스크립트
임베디드 C 코드 의미 기반 정적 분석 프로젝트
"""

import subprocess
import sys
import os

def check_requirements():
    """필수 패키지 확인"""
    required = ['requests', 'matplotlib', 'numpy']
    missing = []
    
    for package in required:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)
    
    if missing:
        print(f"Missing packages: {', '.join(missing)}")
        print(f"Install with: pip install {' '.join(missing)}")
        return False
    return True

def check_ollama():
    """Ollama 서버 확인"""
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            print("✓ Ollama server is running")
            return True
    except:
        pass
    
    print("Ollama server not detected at http://localhost:11434")
    print("   Model 2 and 3 will require Ollama with Qwen model installed")
    print("   To install: https://ollama.ai/")
    print("   Then run: ollama pull qwen2.5-coder:7b")
    return False

def run_step(step_name: str, script: str):
    """단계별 실행"""
    print(f"\n{'='*60}")
    print(f"STEP: {step_name}")
    print('='*60)
    
    result = subprocess.run([sys.executable, script])
    
    if result.returncode != 0:
        print(f"Error in {step_name}")
        return False
    
    print(f"✓ {step_name} completed")
    return True

def main():
    print("""
╔═══════════════════════════════════════════════════════════╗
║   임베디드 C 코드 의미 기반 정적 분석 프로젝트                  ║
║   Semantic Static Analysis for Embedded C Code            ║
╚═══════════════════════════════════════════════════════════╝
    """)
    
    # 환경 확인
    print("Checking environment...")
    if not check_requirements():
        sys.exit(1)
    
    ollama_available = check_ollama()
    
    print("\n" + "="*60)
    print("EXECUTION PLAN")
    print("="*60)
    print("1. Generate synthetic embedded C code dataset")
    print("2. Run Model 1: Regex-based Static Analyzer")
    print("3. Run Model 2: Vanilla LLM (requires Ollama)" + ("" if ollama_available else " - SKIP"))
    print("4. Run Model 3: Enhanced LLM (requires Ollama)" + ("" if ollama_available else " - SKIP"))
    print("5. Compare and evaluate all models")
    print("="*60)
    
    response = input("\nProceed? (y/n): ").lower()
    if response != 'y':
        print("Aborted.")
        sys.exit(0)
    
    # Step 1: 데이터셋 생성
    if not run_step("Dataset Generation", "./dataset_generator.py"):
        sys.exit(1)
    
    # Step 2: Regex 모델
    if not run_step("Model 1: Regex Analyzer", "./model1_regex_analyzer.py"):
        sys.exit(1)
    
    # Step 3 & 4 & 5: LLM 모델들 (Ollama 사용 가능 시)
    if ollama_available:
        run_llm = input("\nRun LLM models? This may take several minutes (y/n): ").lower()
        if run_llm == 'y':
            if not run_step("Model 2: Vanilla LLM", "model2_vanilla_llm.py"):
                print("Model 2 failed, continuing...")
            
            if not run_step("Model 3: Enhanced LLM", "model3_enhanced_llm.py"):
                print("Model 3 failed, continuing...")

            if not run_step("Model 4: Hybrid Analyzer", "model4_hybrid_analyzer.py"):
                print("Model 3 failed, continuing...")

    else:
        print("\nSkipping LLM models (Ollama not available)")
        print("   You can run them later with:")
        print("   python model2_vanilla_llm.py")
        print("   python model3_enhanced_llm.py")
        print("   python model4_hybrid_analyzer.py")
    
    # Step 5: 비교 및 평가
    if os.path.exists("./regex_results.json"):
        if not run_step("Model Comparison", "model_comparator.py"):
            print("Comparison failed")
    
    print(f"\n{'='*60}")
    print("✓ EXECUTION COMPLETE")
    print('='*60)
    print("\nGenerated files:")
    print("  - embedded_c_dataset.json (데이터셋)")
    print("  - regex_results.json (Model 1 결과)")
    
    if ollama_available:
        print("  - vanilla_llm_results.json (Model 2 결과)")
        print("  - enhanced_llm_results.json (Model 3 결과)")
        print("  - hybrid_results.json (Model 4 결과)")
    
    print("  - comparison_report.json (비교 리포트)")
    print("  - model_comparison.png (비교 그래프)")
    
    print("\nCheck comparison_report.json for detailed analysis")

if __name__ == "__main__":
    main()
