#!/usr/bin/env python3
"""
Ollama 연결 테스트 스크립트
Model 2와 Model 3가 제대로 작동하는지 확인
"""

import sys

def test_ollama_import():
    """ollama 패키지 import 테스트"""
    try:
        import ollama
        print("✓ ollama 패키지 import 성공")
        return True
    except ImportError:
        print("✗ ollama 패키지를 찾을 수 없습니다")
        print("  설치: pip install ollama")
        return False

def test_ollama_connection():
    """Ollama 서버 연결 테스트"""
    try:
        import ollama
        models = ollama.list()
        print("✓ Ollama 연결 성공")
        return models
    except Exception as e:
        print(f"✗ Ollama 연결 실패: {e}")
        print("  Ollama를 설치하고 실행하세요: https://ollama.ai/")
        return None

def test_qwen_model(models):
    """Qwen 모델 확인"""
    if not models:
        return False
    
    model_names = [m['name'] for m in models.get('models', [])]
    print(f"\n사용 가능한 모델: {len(model_names)}개")
    for name in model_names[:5]:  # 처음 5개만 출력
        print(f"  - {name}")
    
    qwen_models = [name for name in model_names if 'qwen2.5-coder' in name]
    if qwen_models:
        print(f"\n✓ Qwen 2.5 Coder 모델 발견: {qwen_models[0]}")
        return True
    else:
        print("\n✗ Qwen 2.5 Coder 모델을 찾을 수 없습니다")
        print("  설치: ollama pull qwen2.5-coder:7b")
        return False

def test_simple_generation():
    """간단한 생성 테스트"""
    try:
        import ollama
        
        print("\n간단한 생성 테스트 중...")
        response = ollama.generate(
            model='qwen2.5-coder:7b',
            prompt='Say "Hello, I am ready!" in one sentence.',
            options={'num_predict': 20}
        )
        
        print(f"✓ 생성 성공: {response['response']}")
        return True
    except Exception as e:
        print(f"✗ 생성 실패: {e}")
        return False

def main():
    print("="*60)
    print("Ollama 통합 테스트")
    print("="*60)
    
    # Step 1: Import 테스트
    print("\n[1/4] ollama 패키지 확인...")
    if not test_ollama_import():
        sys.exit(1)
    
    # Step 2: 연결 테스트
    print("\n[2/4] Ollama 서버 연결 확인...")
    models = test_ollama_connection()
    if not models:
        sys.exit(1)
    
    # Step 3: 모델 확인
    print("\n[3/4] Qwen 모델 확인...")
    if not test_qwen_model(models):
        sys.exit(1)
    
    # Step 4: 생성 테스트
    print("\n[4/4] LLM 생성 테스트...")
    if not test_simple_generation():
        sys.exit(1)
    
    print("\n" + "="*60)
    print("✓ 모든 테스트 통과!")
    print("="*60)
    print("\nModel 2와 Model 3를 실행할 준비가 되었습니다:")
    print("  python model2_vanilla_llm.py")
    print("  python model3_enhanced_llm.py")

if __name__ == "__main__":
    main()
