# Semantic Static Analysis for Embedded C Code

---

## Project Overview

### Research Topic
Vulnerability Detection through Semantics-Based Static Analysis of Embedded C Code

### Novel Hypothesis
**Regex-based static analysis relies on syntactic patterns and therefore has limitations in detecting the intent of semantically risky code. An LLM enhanced with static analysis perspectives can overcome these limitations by understanding the behavioral intent of the code.**

---

## Project Structure

### Dataset
- **Synthetic Embedded C Code Dataset**
  - 50 benign code samples
  - 50 semantically risky code samples
  - 100 samples in total

### Three Models

#### Model 1: Regex-Based Static Analyzer (Baseline)
- Traditional pattern-matching approach
- Detection based on syntactic features
- **Limitation**: Difficulty in detecting semantic vulnerabilities

#### Model 2: Vanilla LLM (Qwen via Ollama)
- Code analysis using a base LLM
- Leverages pre-trained knowledge
- **Characteristic**: General code understanding capability

#### Model 3: Static Analysis-Enhanced LLM
- LLM enhanced with static analysis domain knowledge
- Specialized in detecting semantic vulnerabilities
- **Characteristic**: Understanding code intent and execution flow

---

## Quick Start

### 1. Environment Setup

```bash
# Install required packages
pip install ollama matplotlib numpy

# Install Ollama (required to run Models 2 and 3)
# Install from https://ollama.ai/

# Download the Qwen model
ollama pull qwen2.5-coder:7b
```

### 2. Run the Full Pipeline

```bash
python run_analysis.py
```

This script is executed in the following order:
1. Dataset generation
2. Run Model 1 (Regex)
3. Run Model 2 (Vanilla LLM) – requires Ollama
4. Run Model 3 (Enhanced LLM) – requires Ollama
5. Result comparison and evaluation

### 3. 개별 실행

```bash
# Generate dataset only
python dataset_generator.py

# Run Model 1 only
python model1_regex_analyzer.py

# Run Model 2 only (requires Ollama)
python model2_vanilla_llm.py

# Run Model 3 only (requires Ollama)
python model3_enhanced_llm.py

# Compare results
python model_comparator.py
```

---

## Output Files

### Data Files
- `embedded_c_dataset.json`: Generated dataset
- `regex_results.json`: Analysis results from Model 1
- `vanilla_llm_results.json`: Analysis results from Model 2
- `enhanced_llm_results.json`Analysis results from Model 3

### Analysis Results
- `comparison_report.json`: Model performance comparison report
- `model_comparison.png`: Performance comparison graph

---

## 🔬 Dataset Characteristics

### Benign Code Examples
- Proper boundary checks
- NULL pointer validation
- Safe memory management
- Correct type casting

### Risky Code Examples (Semantic Vulnerabilities)

#### 1. Off-by-one Error
```c
// Condition exists, but contains a logical error
for (int i = 0; i <= len; i++) {  // Risk: i <= len
    buffer[i] = data[i];
}
```

#### 2. Race Condition
```c
// Modification of a shared variable without atomicity
uint32_t temp = shared_counter;
temp++;
shared_counter = temp;  // Potential conflict with ISR
```

#### 3. Nested Pointer Dereference
```c
if (config->mode == MODE_ENABLED) {
    config->settings->baudrate = 115200;  // No NULL check for settings
}
```

#### 4. Integer Overflow
```c
// Potential multiplication overflow
uint16_t total_size = num_sensors * sizeof(sensor_t);
sensor_array = malloc(total_size);
```

#### 5. TOCTOU (Time-of-Check to Time-of-Use)
```c
if (device_ready()) {  // Check
    delay_ms(10);
    device_write(data, len);  // Use – state may change in between
}
```

---

## Evaluation Metrics

Each model is evaluated using the following metrics:

- **Accuracy**: Overall correctness
- **Precision**: Proportion of truly risky cases among those predicted as risky
- **Recall**: Proportion of actual risky cases that were correctly detected
- **F1 Score**: Harmonic mean of Precision and Recall

### Confusion Matrix
```
                Predicted
              Safe  Dangerous
Actual Safe    TN      FP
    Dangerous  FN      TP
```

---

## Hypothesis Validation

### Validation Points

1. **Limitations of the Regex Model**
   - Semantic bugs are difficult to detect using only syntactic patterns
   - Expected to have a high false negative rate

2. **Performance of the Vanilla LLM**
   - Improved performance over Regex due to semantic code understanding
   - However, lacks domain-specific expertise

3. **Superiority of the Enhanced LLM**
   - Detects semantic vulnerabilities by applying static analysis principles
   - Expected to achieve high Recall and Precision

### Expected Results
```
Model 1 (Regex)     : Low Recall (misses semantic bugs)
Model 2 (Vanilla)   : Medium Performance
Model 3 (Enhanced)  : High Recall & Precision
```

---

## Technology Stack

- **Python 3.8+**
- **Ollama Python Library**: LLM inference interface
- **Qwen 2.5 Coder 7B**: Code-specialized LLM
- **Matplotlib**: Visualization
- **NumPy**: Numerical computation

---

## Project Structure

```
embedded-c-static-analysis/
├── run_analysis.py              # Main execution script
├── dataset_generator.py         # Dataset generator
├── model1_regex_analyzer.py     # Model 1: Regex
├── model2_vanilla_llm.py        # Model 2: Vanilla LLM
├── model3_enhanced_llm.py       # Model 3: Enhanced LLM
├── model_comparator.py          # Model comparison tool
├── README.md                    # This document
│
├── embedded_c_dataset.json      # Generated dataset
├── regex_results.json           # Model 1 results
├── vanilla_llm_results.json     # Model 2 results
├── enhanced_llm_results.json    # Model 3 results
├── comparison_report.json       # Comparison report
└── model_comparison.png         # Comparison graph
```

---

## Detailed Analysis Guide

### Model 1 (Regex) Analysis
```python
from model1_regex_analyzer import RegexStaticAnalyzer

analyzer = RegexStaticAnalyzer()
result = analyzer.analyze(your_code)
print(result['findings'])
```

### Model 2 (Vanilla LLM) Analysis
```python
from model2_vanilla_llm import VanillaLLMAnalyzer

analyzer = VanillaLLMAnalyzer()
result = analyzer.analyze(your_code)
print(result['reasoning'])
```

### Model 3 (Enhanced LLM) Analysis
```python
from model3_enhanced_llm import StaticAnalysisEnhancedLLM

analyzer = StaticAnalysisEnhancedLLM()
result = analyzer.analyze(your_code)
print(result['semantic_issues'])
```

---

## Usage Example

### Analyzing New Code

```python
code_sample = """
void process_data(uint8_t *input, int len) {
    for (int i = 0; i <= len; i++) {  // Suspicious part
        buffer[i] = input[i];
    }
}
"""

# Analysis with the Enhanced LLM
from model3_enhanced_llm import StaticAnalysisEnhancedLLM

analyzer = StaticAnalysisEnhancedLLM()
result = analyzer.analyze(code_sample)

print(f"Lisk Level: {result['prediction']}")
print(f"Confidence: {result['confidence']}")
print(f"Detected Issues: {result['semantic_issues']}")
print(f"Detailed Explanation: {result['reasoning']}")
```

---

## References

### Static Analysis Principles
- Buffer overflow detection
- Race condition analysis
- Pointer safety verification
- Integer overflow prevention
- Memory leak detection

### Embedded System Characteristics
- Interrupt handling
- Concurrent access patterns
- Resource constraints
- Real-time requirements

---

## Notes and Considerations

1. **Ollama Setup**
   - Ollama must be installed to run Models 2 and 3
   - Python Ollama package required: pip install ollama
   - Model download required: ollama pull qwen2.5-coder:7b

2. **Execution Time**
   - LLM models take approximately 1–2 seconds per sample
   - Full dataset analysis (100 samples) takes about 3–5 minutes

3. **Memory Requirements**
   - Qwen 7B model: at least 8 GB RAM recommended

---

## License

MIT License

---

