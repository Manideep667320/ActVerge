# ActVerge Evaluation & Benchmark Suite

This directory contains the benchmarking harness and empirical evaluation pipeline for ActVerge, evaluated against **100 controlled real-world scenarios** derived from **Mind2Web** task patterns with deliberate failure injections.

---

## 📊 Benchmark Summary

| Metric | ActVerge Oracle | Raw Agent Baseline | Delta / Impact |
|---|:---:|:---:|:---:|
| **Overall Classification Accuracy** | **83.00%** | ~55.0% *(self-reported)* | **+28.0% gain** over unverified self-reports |
| **Fatal Failure Interception (Recall)** | **100.00%** | 0.0% *(undetected)* | **30 out of 30** catastrophic errors caught |
| **False Success Rate (Silent Failures)** | **10.77%** | 100.0% *(all unverified)* | **89.23%** of silent failures intercepted |
| **False Alarm Rate** | **5.71%** | N/A | Low false rejection of true successes |
| **Mean Verification Latency** | **3.07 s** | N/A | Sub-5s multi-modal state synthesis |
| **Evaluated Scenarios** | **100 tasks** | N/A | Balanced across 4 web agent domains |

---

## 🎯 True 4x4 Multi-Class Confusion Matrix ($N = 100$)

```
Actual \ Predicted    SUCCESS      PARTIAL      FAILED       UNCERTAIN    TOTAL
-----------------------------------------------------------------------------
SUCCESS               32           1            2            0            35
PARTIAL               4            21           0            0            25
FAILED                0            0            30           0            30
UNCERTAIN             3            5            2            0            10
-----------------------------------------------------------------------------
TOTAL                 39           27           34           0            100
```

### Classification Performance Metrics
- **SUCCESS**: Precision = **82.1%**, Recall = **91.4%**, F1 = **86.5%** (Support: 35)
- **PARTIAL**: Precision = **77.8%**, Recall = **84.0%**, F1 = **80.8%** (Support: 25)
- **FAILED**: Precision = **88.2%**, Recall = **100.0%**, F1 = **93.8%** (Support: 30)
- **UNCERTAIN**: Precision = 0.0%, Recall = 0.0%, F1 = 0.0% (Support: 10)
- **Macro Average**: Precision = **62.0%**, Recall = **68.9%**, F1 = **65.3%**
- **Weighted Average**: Precision = **74.6%**, Recall = **83.0%**, F1 = **78.6%**

---

## ⏱️ Central Tendency Statistics

| Metric | Mean ($\mu$) | Median ($M$) | Mode | IQR | Std Dev ($\sigma$) | P95 |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Verification Latency** | **3.073 s** | **2.962 s** | 2.033 s | 0.858 s | $\pm 0.924\text{ s}$ | 4.960 s |
| **Execution Steps / Task** | **1.36** | **1.00** | 1.0 | 1.0 | $\pm 0.63$ | 3.0 |
| **DOM Evidence Size** | **203.1 chars** | **199.0 chars** | 162.0 | 79.8 | $\pm 56.4\text{ chars}$ | 294.0 |
| **Confidence Score** | **0.936** | **0.950** | 0.95 | 0.05 | $\pm 0.024$ | 0.95 |

---

## 📈 Correlation Statistics (Pearson's $r$)

| Variable Pair | Pearson $r$ | $p$-value | Empirical Finding |
| :--- | :---: | :---: | :--- |
| **Execution Steps vs. Verification Latency** | **+0.101** | $0.3168$ | Weak positive correlation; latency is dominated by LLM response time rather than trace length. |
| **DOM Evidence Length vs. Verification Latency** | **+0.180** | $0.0726$ | Marginal positive trend ($p < 0.10$); larger DOM context prompts take slightly longer to process. |
| **Execution Steps vs. Classification Accuracy** | **+0.133** | $0.1873$ | Independence observed; verification quality is robust across single-step and multi-step tasks. |
| **Verifier Confidence vs. Classification Accuracy** | **+0.183** | $0.0680$ | Positive alignment; higher model confidence correlates with correct classification. |

---

## 📦 Dataset Structure: `curated_test_set.json`

The 100-scenario dataset is structured as:
- **E-Commerce & Retail** (30 tasks)
- **Productivity & Workspaces** (25 tasks)
- **Developer Tools & Cloud** (25 tasks)
- **Travel & Logistics** (20 tasks)

Each task record contains:
```json
{
  "task_id": "ecom_001",
  "domain": "E-Commerce",
  "user_task": "Add Nike Air Max running shoes (Size 10, Black) to the cart and proceed to checkout.",
  "ground_truth": "SUCCESS",
  "failure_variant": null,
  "action_trace": [...],
  "evidence_package": {
    "url": "https://nike.example.com/checkout",
    "dom_summary": "[H1: Checkout] [Item: Nike Air Max (Size 10, Black)] [Total: $140.00] [Button: Place Order (active)]",
    "inputs": {"email": "user@example.com", "zip": "94103"},
    "buttons": ["Place Order", "Apply Coupon"],
    "alerts": []
  }
}
```

---

## 🚀 Running the Benchmarks Locally

### 1. Build / Validate Benchmark Dataset
```bash
python evaluation/benchmark/build_benchmark_dataset.py
```

### 2. Execute Full Statistical Benchmark Harness
```bash
python evaluation/scripts/run_benchmark.py
```

Outputs are automatically generated in:
- `evaluation/results/benchmark_eval_results.json` (raw per-task metrics and statistical summaries)
- `evaluation/results/evaluation_report.md` (publication-ready markdown tables)
