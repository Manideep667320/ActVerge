"""
metrics.py
==========
Evaluation metric functions for the ActVerge benchmark harness.

All functions operate on lists of string labels drawn from:
    {"SUCCESS", "PARTIAL", "FAILED", "UNCERTAIN"}

Usage
-----
    from evaluation.scripts.metrics import generate_report

    report = generate_report(results)
    print(report)
"""

from __future__ import annotations

import statistics
from typing import Literal

Label = Literal["SUCCESS", "PARTIAL", "FAILED", "UNCERTAIN"]


# ── Individual metric functions ────────────────────────────────────────────────


def outcome_accuracy(predictions: list[Label], ground_truth: list[Label]) -> float:
    """Fraction of predictions that exactly match the ground-truth label.

    Parameters
    ----------
    predictions : list[Label]
        Labels predicted by the system under evaluation.
    ground_truth : list[Label]
        Human-annotated ground-truth labels.

    Returns
    -------
    float
        Accuracy in [0.0, 1.0].  Returns 0.0 for empty inputs.
    """
    if not predictions:
        return 0.0
    correct = sum(p == g for p, g in zip(predictions, ground_truth))
    return correct / len(predictions)


def false_success_rate(predictions: list[Label], ground_truth: list[Label]) -> float:
    """Fraction of true failures (FAILED/PARTIAL) labelled as SUCCESS.

    A false success is the most dangerous error class — the agent believes it
    completed the task when it did not.

    Parameters
    ----------
    predictions : list[Label]
        Labels predicted by the system under evaluation.
    ground_truth : list[Label]
        Human-annotated ground-truth labels.

    Returns
    -------
    float
        False-success rate in [0.0, 1.0].  Returns 0.0 if no true failures exist.
    """
    true_failures = [
        p for p, g in zip(predictions, ground_truth)
        if g in ("FAILED", "PARTIAL")
    ]
    if not true_failures:
        return 0.0
    false_successes = sum(p == "SUCCESS" for p in true_failures)
    return false_successes / len(true_failures)


def false_failure_rate(predictions: list[Label], ground_truth: list[Label]) -> float:
    """Fraction of true successes labelled as FAILED.

    Parameters
    ----------
    predictions : list[Label]
        Labels predicted by the system under evaluation.
    ground_truth : list[Label]
        Human-annotated ground-truth labels.

    Returns
    -------
    float
        False-failure rate in [0.0, 1.0].  Returns 0.0 if no true successes exist.
    """
    true_successes = [
        p for p, g in zip(predictions, ground_truth)
        if g == "SUCCESS"
    ]
    if not true_successes:
        return 0.0
    false_failures = sum(p == "FAILED" for p in true_successes)
    return false_failures / len(true_successes)


def uncertainty_quality(predictions: list[Label], ground_truth: list[Label]) -> float:
    """Precision of UNCERTAIN predictions — how often UNCERTAIN maps to truly
    ambiguous ground-truth (PARTIAL or UNCERTAIN).

    A high score means the system correctly reserves uncertainty for cases
    that are genuinely hard to call.

    Parameters
    ----------
    predictions : list[Label]
        Labels predicted by the system under evaluation.
    ground_truth : list[Label]
        Human-annotated ground-truth labels.

    Returns
    -------
    float
        Uncertainty quality score in [0.0, 1.0].
        Returns 1.0 if no UNCERTAIN predictions were made (vacuously true).
    """
    uncertain_preds = [
        g for p, g in zip(predictions, ground_truth)
        if p == "UNCERTAIN"
    ]
    if not uncertain_preds:
        return 1.0
    truly_ambiguous = sum(g in ("PARTIAL", "UNCERTAIN") for g in uncertain_preds)
    return truly_ambiguous / len(uncertain_preds)


def verification_latency_stats(latencies: list[float]) -> dict:
    """Compute descriptive statistics for verification pipeline latency.

    Parameters
    ----------
    latencies : list[float]
        Per-task end-to-end verification latency in seconds.

    Returns
    -------
    dict
        Keys: mean, median, stdev, p95, p99, min, max (all in seconds).
        Returns a dict of zeros for empty input.
    """
    if not latencies:
        return {k: 0.0 for k in ("mean", "median", "stdev", "p95", "p99", "min", "max")}

    sorted_lat = sorted(latencies)
    n = len(sorted_lat)

    def percentile(data: list[float], pct: float) -> float:
        idx = int(pct / 100.0 * n)
        return data[min(idx, n - 1)]

    return {
        "mean": statistics.mean(latencies),
        "median": statistics.median(latencies),
        "stdev": statistics.stdev(latencies) if n > 1 else 0.0,
        "p95": percentile(sorted_lat, 95),
        "p99": percentile(sorted_lat, 99),
        "min": sorted_lat[0],
        "max": sorted_lat[-1],
    }


def generate_report(results: list[dict]) -> dict:
    """Generate a full metrics report from a list of per-task result dicts.

    Each result dict must contain:
        - "prediction"  : Label predicted by the system
        - "ground_truth": Human-annotated ground-truth label
        - "latency_s"   : Verification latency in seconds (float)

    Parameters
    ----------
    results : list[dict]
        List of per-task result records.

    Returns
    -------
    dict
        Aggregated metrics report with keys:
        - outcome_accuracy
        - false_success_rate
        - false_failure_rate
        - uncertainty_quality
        - latency (nested dict from verification_latency_stats)
        - n_tasks
    """
    predictions: list[Label] = [r["prediction"] for r in results]
    ground_truth: list[Label] = [r["ground_truth"] for r in results]
    latencies: list[float] = [r.get("latency_s", 0.0) for r in results]

    return {
        "n_tasks": len(results),
        "outcome_accuracy": outcome_accuracy(predictions, ground_truth),
        "false_success_rate": false_success_rate(predictions, ground_truth),
        "false_failure_rate": false_failure_rate(predictions, ground_truth),
        "uncertainty_quality": uncertainty_quality(predictions, ground_truth),
        "latency": verification_latency_stats(latencies),
    }
