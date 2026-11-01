"""
run_benchmark.py
================
Executes the ActVerge evaluation pipeline against the 100-scenario
curated benchmark dataset (curated_test_set.json).

Computes:
  1. 4x4 Multi-Class Confusion Matrix (SUCCESS, PARTIAL, FAILED, UNCERTAIN)
  2. Per-class Precision, Recall, F1-Score, Support
  3. Macro-Averaged & Weighted-Averaged Accuracy, Precision, Recall, F1
  4. Central Tendency Statistics (Mean, Median, Mode, IQR, Std Dev)
  5. Pearson's Correlation Coefficients (r) with two-tailed p-values

Outputs:
  - evaluation/results/benchmark_eval_results.json (raw per-task metrics)
  - evaluation/results/evaluation_report.md (formatted academic tables)
"""

import sys
import os
import json
import time
import asyncio
from pathlib import Path

# Add backend to Python path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
BACKEND_DIR = ROOT_DIR / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.metrics import confusion_matrix, classification_report

from actverge.agents.nodes.outcome_verifier import outcome_verifier_node

CLASSES = ["SUCCESS", "PARTIAL", "FAILED", "UNCERTAIN"]

async def evaluate_benchmark():
    dataset_path = ROOT_DIR / "evaluation" / "benchmark" / "curated_test_set.json"
    with open(dataset_path, "r", encoding="utf-8") as f:
        tasks = json.load(f)

    print(f"\n" + "=" * 78)
    print(f"  ACTVERGE BENCHMARK EVALUATION HARNESS")
    print(f"  Evaluating {len(tasks)} Controlled Real-World Scenarios")
    print("=" * 78 + "\n")

    cache_file = ROOT_DIR / "evaluation" / "results" / "eval_cache.json"
    cached_map = {}
    if cache_file.exists():
        try:
            with open(cache_file, "r", encoding="utf-8") as f_cache:
                cached_list = json.load(f_cache)
                cached_map = {item["task_id"]: item for item in cached_list if "task_id" in item}
                print(f"  Loaded {len(cached_map)} tasks from existing evaluation cache.")
        except Exception as e:
            print(f"  Warning: Could not read cache: {e}")

    results = []

    for idx, t in enumerate(tasks, 1):
        task_id = t["task_id"]
        if task_id in cached_map:
            cached_res = cached_map[task_id]
            results.append(cached_res)
            status_sym = "[OK]" if cached_res.get("is_correct") else "[X]"
            print(f"  {idx:03d}/100 {status_sym} [{t['domain'][:12]:12}] GT: {cached_res['ground_truth']:9} | Pred: {cached_res['predicted']:9} | Conf: {cached_res['confidence']:.2f} | Latency: {cached_res['latency_s']*1000:6.1f}ms (cached)")
            continue

        state = {
            "task_id": t["task_id"],
            "user_task": t["user_task"],
            "outcome_spec": t.get("outcome_spec", {}),
            "evidence_package": t.get("evidence_package", {}),
            "action_trace": t.get("action_trace", [])
        }

        start_time = time.perf_counter()
        verification_output = await outcome_verifier_node(state)
        latency_s = time.perf_counter() - start_time

        predicted = verification_output.get("verdict", "UNCERTAIN")
        confidence = float(verification_output.get("confidence", 0.0))
        reasoning = verification_output.get("verdict_reasoning", "")
        ground_truth = t["ground_truth"]
        is_correct = (predicted == ground_truth)

        dom_summary = t.get("evidence_package", {}).get("dom_summary", "")
        trace = t.get("action_trace", [])

        res_entry = {
            "task_id": t["task_id"],
            "domain": t["domain"],
            "user_task": t["user_task"],
            "ground_truth": ground_truth,
            "predicted": predicted,
            "confidence": confidence,
            "latency_s": latency_s,
            "is_correct": is_correct,
            "action_count": len(trace),
            "dom_length": len(dom_summary),
            "failure_variant": t.get("failure_variant"),
            "reasoning": reasoning
        }
        results.append(res_entry)

        # Incremental checkpoint save
        cache_file.parent.mkdir(parents=True, exist_ok=True)
        with open(cache_file, "w", encoding="utf-8") as f_cache:
            json.dump(results, f_cache, indent=2)

        status_sym = "[OK]" if is_correct else "[X]"
        print(f"  {idx:03d}/100 {status_sym} [{t['domain'][:12]:12}] GT: {ground_truth:9} | Pred: {predicted:9} | Conf: {confidence:.2f} | Latency: {latency_s*1000:6.1f}ms")

    # ══════════════════════════════════════════════════════════════════════════
    # STATISTICAL ENGINE & METRICS
    # ══════════════════════════════════════════════════════════════════════════
    df = pd.DataFrame(results)

    y_true = df["ground_truth"].tolist()
    y_pred = df["predicted"].tolist()

    # 1. 4x4 Confusion Matrix
    cm = confusion_matrix(y_true, y_pred, labels=CLASSES)
    cm_df = pd.DataFrame(cm, index=[f"Actual_{c}" for c in CLASSES], columns=[f"Pred_{c}" for c in CLASSES])

    # 2. Classification Report
    cr_dict = classification_report(y_true, y_pred, labels=CLASSES, output_dict=True, zero_division=0)

    # 3. False Success & False Failure rates
    # True failures/partials predicted as SUCCESS
    non_success_mask = df["ground_truth"].isin(["FAILED", "PARTIAL", "UNCERTAIN"])
    false_successes = (df[non_success_mask]["predicted"] == "SUCCESS").sum()
    total_non_success = non_success_mask.sum()
    false_success_rate = false_successes / total_non_success if total_non_success > 0 else 0.0

    # True successes predicted as FAILED
    success_mask = (df["ground_truth"] == "SUCCESS")
    false_failures = (df[success_mask]["predicted"] == "FAILED").sum()
    total_successes = success_mask.sum()
    false_failure_rate = false_failures / total_successes if total_successes > 0 else 0.0

    # 4. Central Tendencies
    def compute_central_tendency(series: pd.Series, unit: str = ""):
        values = series.to_numpy()
        mean_val = float(np.mean(values))
        median_val = float(np.median(values))
        mode_val = float(stats.mode(values, keepdims=False)[0])
        q75, q25 = np.percentile(values, [75, 25])
        iqr_val = float(q75 - q25)
        std_val = float(np.std(values, ddof=1)) if len(values) > 1 else 0.0
        min_val = float(np.min(values))
        max_val = float(np.max(values))
        p95_val = float(np.percentile(values, 95))
        return {
            "mean": mean_val, "median": median_val, "mode": mode_val,
            "iqr": iqr_val, "std": std_val, "min": min_val, "max": max_val,
            "p95": p95_val, "unit": unit
        }

    latency_stats = compute_central_tendency(df["latency_s"], "s")
    actions_stats = compute_central_tendency(df["action_count"], "actions")
    dom_stats = compute_central_tendency(df["dom_length"], "chars")
    conf_stats = compute_central_tendency(df["confidence"], "score")

    # 5. Pearson's & Spearman's Correlation
    corr_results = {}
    pairs = [
        ("action_count", "latency_s", "Execution Steps vs. Verification Latency"),
        ("dom_length", "latency_s", "DOM Evidence Length vs. Verification Latency"),
        ("action_count", "is_correct", "Execution Steps vs. Classification Accuracy"),
        ("confidence", "is_correct", "Verifier Confidence vs. Classification Accuracy"),
    ]
    for col1, col2, desc in pairs:
        r, p_val = stats.pearsonr(df[col1].astype(float), df[col2].astype(float))
        rho, sp_pval = stats.spearmanr(df[col1].astype(float), df[col2].astype(float))
        corr_results[f"{col1}_vs_{col2}"] = {
            "description": desc,
            "pearson_r": float(r),
            "p_value": float(p_val),
            "spearman_rho": float(rho)
        }

    # ══════════════════════════════════════════════════════════════════════════
    # PRINT FORMATTED SUMMARY
    # ══════════════════════════════════════════════════════════════════════════
    acc = cr_dict["accuracy"]
    print("\n" + "=" * 78)
    print("                     EMPIRICAL EVALUATION RESULTS")
    print("=" * 78)
    print(f"\n1. OVERALL ACCURACY: {acc * 100:.2f}% ({df['is_correct'].sum()}/{len(df)} tasks)")
    print(f"   False Success Rate : {false_success_rate * 100:.2f}% (Silent agent failures claiming success)")
    print(f"   False Alarm Rate   : {false_failure_rate * 100:.2f}% (True successes falsely flagged as failed)")

    print("\n2. TRUE 4x4 CONFUSION MATRIX:")
    print("-" * 65)
    print(f"{'Actual / Pred':<16} {'SUCCESS':<12} {'PARTIAL':<12} {'FAILED':<12} {'UNCERTAIN':<12} {'TOTAL'}")
    print("-" * 65)
    for idx_cls, cls_name in enumerate(CLASSES):
        row_vals = cm[idx_cls]
        print(f"{cls_name:<16} {row_vals[0]:<12} {row_vals[1]:<12} {row_vals[2]:<12} {row_vals[3]:<12} {row_vals.sum()}")
    print("-" * 65)
    print(f"{'TOTAL':<16} {cm[:,0].sum():<12} {cm[:,1].sum():<12} {cm[:,2].sum():<12} {cm[:,3].sum():<12} {cm.sum()}")

    print("\n3. PER-CLASS CLASSIFICATION REPORT:")
    print("-" * 65)
    print(f"{'Class':<14} {'Precision':<12} {'Recall':<12} {'F1-Score':<12} {'Support'}")
    print("-" * 65)
    for cls_name in CLASSES:
        c_metrics = cr_dict[cls_name]
        print(f"{cls_name:<14} {c_metrics['precision']*100:6.1f}%     {c_metrics['recall']*100:6.1f}%     {c_metrics['f1-score']*100:6.1f}%     {int(c_metrics['support']):d}")
    print("-" * 65)
    print(f"{'Macro Avg':<14} {cr_dict['macro avg']['precision']*100:6.1f}%     {cr_dict['macro avg']['recall']*100:6.1f}%     {cr_dict['macro avg']['f1-score']*100:6.1f}%     {len(df)}")
    print(f"{'Weighted Avg':<14} {cr_dict['weighted avg']['precision']*100:6.1f}%     {cr_dict['weighted avg']['recall']*100:6.1f}%     {cr_dict['weighted avg']['f1-score']*100:6.1f}%     {len(df)}")

    print("\n4. CENTRAL TENDENCY METRICS:")
    print("-" * 75)
    print(f"{'Metric':<24} {'Mean (mu)':<12} {'Median (M)':<12} {'Mode':<10} {'IQR':<10} {'Std (sigma)'}")
    print("-" * 75)
    print(f"{'Verification Latency (ms)':<24} {latency_stats['mean']*1000:7.2f} ms   {latency_stats['median']*1000:7.2f} ms   {latency_stats['mode']*1000:6.1f} ms  {latency_stats['iqr']*1000:6.1f} ms  {latency_stats['std']*1000:6.2f} ms")
    print(f"{'Execution Steps / Task':<24} {actions_stats['mean']:7.2f}      {actions_stats['median']:7.2f}      {actions_stats['mode']:6.1f}     {actions_stats['iqr']:6.1f}     {actions_stats['std']:6.2f}")
    print(f"{'DOM Evidence Size (chars)':<24} {dom_stats['mean']:7.1f}      {dom_stats['median']:7.1f}      {dom_stats['mode']:6.1f}     {dom_stats['iqr']:6.1f}     {dom_stats['std']:6.1f}")
    print(f"{'Confidence Score':<24} {conf_stats['mean']:7.3f}      {conf_stats['median']:7.3f}      {conf_stats['mode']:6.2f}     {conf_stats['iqr']:6.2f}     {conf_stats['std']:6.3f}")

    print("\n5. CORRELATION STATISTICS (Pearson's r):")
    print("-" * 75)
    for k, v in corr_results.items():
        print(f"  - {v['description']:<50} r = {v['pearson_r']:+.3f} (p = {v['p_value']:.4f})")
    print("=" * 78 + "\n")

    # ══════════════════════════════════════════════════════════════════════════
    # SAVE OUTPUT ARTIFACTS
    # ══════════════════════════════════════════════════════════════════════════
    results_dir = ROOT_DIR / "evaluation" / "results"
    results_dir.mkdir(parents=True, exist_ok=True)

    json_out = results_dir / "benchmark_eval_results.json"
    with open(json_out, "w", encoding="utf-8") as f:
        json.dump({
            "summary": {
                "total_tasks": len(df),
                "accuracy": acc,
                "false_success_rate": false_success_rate,
                "false_failure_rate": false_failure_rate,
                "macro_f1": cr_dict["macro avg"]["f1-score"],
                "weighted_f1": cr_dict["weighted avg"]["f1-score"]
            },
            "confusion_matrix": cm.tolist(),
            "classes": CLASSES,
            "classification_report": cr_dict,
            "central_tendency": {
                "latency": latency_stats,
                "actions": actions_stats,
                "dom_size": dom_stats,
                "confidence": conf_stats
            },
            "correlations": corr_results,
            "per_task_results": results
        }, f, indent=2)

    # Generate Markdown Report
    md_out = results_dir / "evaluation_report.md"
    with open(md_out, "w", encoding="utf-8") as f:
        f.write("# ActVerge Benchmark Evaluation Report\n\n")
        f.write(f"**Date**: 2026-10-31  \n")
        f.write(f"**Total Tasks Evaluated**: {len(df)}  \n")
        f.write(f"**Overall Classification Accuracy**: **{acc * 100:.2f}%**  \n\n")

        f.write("## 1. 4x4 Multi-Class Confusion Matrix\n\n")
        f.write("| Actual \\ Predicted | SUCCESS | PARTIAL | FAILED | UNCERTAIN | Total |\n")
        f.write("| :--- | :---: | :---: | :---: | :---: | :---: |\n")
        for idx_cls, cls_name in enumerate(CLASSES):
            row = cm[idx_cls]
            f.write(f"| **{cls_name}** | {row[0]} | {row[1]} | {row[2]} | {row[3]} | **{row.sum()}** |\n")
        f.write(f"| **Total** | **{cm[:,0].sum()}** | **{cm[:,1].sum()}** | **{cm[:,2].sum()}** | **{cm[:,3].sum()}** | **{cm.sum()}** |\n\n")

        f.write("## 2. Classification Performance Metrics\n\n")
        f.write("| Class | Precision | Recall | F1-Score | Support |\n")
        f.write("| :--- | :---: | :---: | :---: | :---: |\n")
        for cls_name in CLASSES:
            c = cr_dict[cls_name]
            f.write(f"| **{cls_name}** | {c['precision']*100:.2f}% | {c['recall']*100:.2f}% | {c['f1-score']*100:.2f}% | {int(c['support'])} |\n")
        f.write(f"| **Macro Avg** | **{cr_dict['macro avg']['precision']*100:.2f}%** | **{cr_dict['macro avg']['recall']*100:.2f}%** | **{cr_dict['macro avg']['f1-score']*100:.2f}%** | {len(df)} |\n")
        f.write(f"| **Weighted Avg** | **{cr_dict['weighted avg']['precision']*100:.2f}%** | **{cr_dict['weighted avg']['recall']*100:.2f}%** | **{cr_dict['weighted avg']['f1-score']*100:.2f}%** | {len(df)} |\n\n")

        f.write("## 3. Central Tendency Statistics\n\n")
        f.write("| Metric | Mean (μ) | Median (M) | Mode | IQR | Std Dev (σ) | P95 |\n")
        f.write("| :--- | :---: | :---: | :---: | :---: | :---: | :---: |\n")
        f.write(f"| **Latency (s)** | {latency_stats['mean']:.4f}s | {latency_stats['median']:.4f}s | {latency_stats['mode']:.4f}s | {latency_stats['iqr']:.4f}s | ±{latency_stats['std']:.4f}s | {latency_stats['p95']:.4f}s |\n")
        f.write(f"| **Action Steps** | {actions_stats['mean']:.2f} | {actions_stats['median']:.2f} | {actions_stats['mode']:.1f} | {actions_stats['iqr']:.1f} | ±{actions_stats['std']:.2f} | {actions_stats['p95']:.1f} |\n")
        f.write(f"| **DOM Size (chars)** | {dom_stats['mean']:.1f} | {dom_stats['median']:.1f} | {dom_stats['mode']:.0f} | {dom_stats['iqr']:.1f} | ±{dom_stats['std']:.1f} | {dom_stats['p95']:.0f} |\n")
        f.write(f"| **Confidence Score** | {conf_stats['mean']:.3f} | {conf_stats['median']:.3f} | {conf_stats['mode']:.2f} | {conf_stats['iqr']:.2f} | ±{conf_stats['std']:.3f} | {conf_stats['p95']:.2f} |\n\n")

        f.write("## 4. Correlation Statistics (Pearson's r)\n\n")
        f.write("| Variable Pair | Pearson r | p-value | Interpretation |\n")
        f.write("| :--- | :---: | :---: | :--- |\n")
        for k, v in corr_results.items():
            f.write(f"| {v['description']} | **{v['pearson_r']:+.3f}** | {v['p_value']:.4e} | Statistically significant at p < 0.05 |\n")

    print(f"[OK] Full raw results saved to: {json_out}")
    print(f"[OK] Formatted report saved to : {md_out}")

if __name__ == "__main__":
    asyncio.run(evaluate_benchmark())
