"""
run_actverge.py
===============
Full ActVerge pipeline evaluation runner.

Loads Mind2Web tasks, submits each task to the ActVerge verification
pipeline (via the backend API), collects results, and logs all metrics
to MLflow.

Usage
-----
    python evaluation/scripts/run_actverge.py \
        [--split test] [--max-tasks 50] [--api-url http://localhost:8000]
"""

from __future__ import annotations

import argparse
import time
import random

import mlflow

from evaluation.benchmark.mind2web_loader import load_mind2web_tasks
from evaluation.scripts.metrics import generate_report

# ── ActVerge pipeline stub ────────────────────────────────────────────────────


def call_actverge_pipeline(task: dict, api_url: str) -> dict:
    """Submit a task to the ActVerge backend and return the verification result.

    TODO: Replace the stub below with a real HTTP call once the backend
          /verify endpoint is implemented.

    Expected response shape:
        {
            "task_id": str,
            "verdict": "SUCCESS" | "PARTIAL" | "FAILED" | "UNCERTAIN",
            "confidence": float,        # 0.0 – 1.0
            "evidence_summary": str,
            "latency_s": float,
        }
    """
    # ── Stub implementation ───────────────────────────────────────────────────
    start = time.monotonic()
    time.sleep(random.uniform(0.5, 3.0))  # simulate network + LLM latency
    elapsed = time.monotonic() - start

    verdict = random.choices(
        ["SUCCESS", "FAILED", "UNCERTAIN", "PARTIAL"],
        weights=[0.55, 0.25, 0.12, 0.08],
    )[0]

    return {
        "task_id": task["task_id"],
        "verdict": verdict,
        "confidence": round(random.uniform(0.6, 0.99), 3),
        "evidence_summary": "stub — real pipeline not yet connected",
        "latency_s": elapsed,
    }
    # ── End stub ──────────────────────────────────────────────────────────────


# ── Runner ────────────────────────────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(description="Run ActVerge pipeline evaluation")
    parser.add_argument("--split", default="test", choices=["train", "validation", "test"])
    parser.add_argument("--max-tasks", type=int, default=50)
    parser.add_argument("--api-url", default="http://localhost:8000")
    args = parser.parse_args()

    print(f"Loading {args.max_tasks} tasks from Mind2Web [{args.split}] split...")
    tasks = load_mind2web_tasks(split=args.split, max_tasks=args.max_tasks)
    print(f"Loaded {len(tasks)} tasks.")

    mlflow.set_experiment("actverge-pipeline")

    with mlflow.start_run(run_name="actverge-full-pipeline"):
        mlflow.log_param("n_tasks", len(tasks))
        mlflow.log_param("split", args.split)
        mlflow.log_param("api_url", args.api_url)

        results = []
        for i, task in enumerate(tasks, 1):
            print(f"  [{i}/{len(tasks)}] task_id={task['task_id'][:12]}...", end=" ")
            out = call_actverge_pipeline(task, args.api_url)
            results.append({
                "task_id": out["task_id"],
                "prediction": out["verdict"],
                "ground_truth": "SUCCESS",  # placeholder until labelled test set
                "latency_s": out["latency_s"],
                "confidence": out["confidence"],
            })
            print(f"verdict={out['verdict']}  ({out['latency_s']:.2f}s)")

        report = generate_report(results)

        mlflow.log_metric("outcome_accuracy", report["outcome_accuracy"])
        mlflow.log_metric("false_success_rate", report["false_success_rate"])
        mlflow.log_metric("false_failure_rate", report["false_failure_rate"])
        mlflow.log_metric("uncertainty_quality", report["uncertainty_quality"])
        mlflow.log_metric("latency_mean", report["latency"]["mean"])
        mlflow.log_metric("latency_p95", report["latency"]["p95"])
        mlflow.log_metric("latency_p99", report["latency"]["p99"])

        print("\n── ActVerge Pipeline Report ──────────────────────────────────")
        print(f"  Tasks evaluated   : {report['n_tasks']}")
        print(f"  Outcome accuracy  : {report['outcome_accuracy']:.3f}")
        print(f"  False success rate: {report['false_success_rate']:.3f}")
        print(f"  False failure rate: {report['false_failure_rate']:.3f}")
        print(f"  Uncertainty quality:{report['uncertainty_quality']:.3f}")
        print(f"  Latency mean (s)  : {report['latency']['mean']:.3f}")
        print(f"  Latency p95  (s)  : {report['latency']['p95']:.3f}")
        print("──────────────────────────────────────────────────────────────")

    print("\n✅ ActVerge evaluation complete. Run `mlflow ui` to view results.")


if __name__ == "__main__":
    main()
