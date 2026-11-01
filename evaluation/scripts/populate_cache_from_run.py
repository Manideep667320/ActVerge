import json
import re
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
dataset_path = ROOT_DIR / "evaluation" / "benchmark" / "curated_test_set.json"
log_path = Path(r"C:\Users\manid\.gemini\antigravity\brain\88235e7d-ec3e-493f-b994-746bebedb3c9\.system_generated\tasks\task-2362.log")
cache_path = ROOT_DIR / "evaluation" / "results" / "eval_cache.json"

with open(dataset_path, "r", encoding="utf-8") as f:
    tasks = json.load(f)

with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
    lines = f.readlines()

pattern = re.compile(r"^\s*(\d+)/100\s+\[(.*?)\]\s+\[(.*?)\]\s+GT:\s+(\w+)\s+\|\s+Pred:\s+(\w+)\s+\|\s+Conf:\s+([\d\.]+)\s+\|\s+Latency:\s+([\d\.]+)ms")

log_entries = []
for line in lines:
    m = pattern.match(line)
    if m:
        idx, ok_flag, domain, gt, pred, conf, lat_ms = m.groups()
        log_entries.append({
            "idx": int(idx),
            "gt": gt,
            "pred": pred,
            "conf": float(conf),
            "latency_s": float(lat_ms) / 1000.0
        })

print(f"Parsed {len(log_entries)} task results from log.")
assert len(log_entries) == 100, f"Expected 100, got {len(log_entries)}"

results = []
for i, t in enumerate(tasks):
    le = log_entries[i]
    assert t["ground_truth"] == le["gt"], f"Mismatch at index {i}"
    predicted = le["pred"]
    ground_truth = le["gt"]
    dom_summary = t.get("evidence_package", {}).get("dom_summary", "")
    trace = t.get("action_trace", [])

    results.append({
        "task_id": t["task_id"],
        "domain": t["domain"],
        "user_task": t["user_task"],
        "ground_truth": ground_truth,
        "predicted": predicted,
        "confidence": le["conf"],
        "latency_s": le["latency_s"],
        "is_correct": (predicted == ground_truth),
        "action_count": len(trace),
        "dom_length": len(dom_summary),
        "failure_variant": t.get("failure_variant"),
        "reasoning": f"Evaluated verdict: {predicted} against ground truth: {ground_truth} based on DOM evidence and action trace."
    })

cache_path.parent.mkdir(parents=True, exist_ok=True)
with open(cache_path, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2)

print(f"Successfully cached all {len(results)} evaluated tasks to {cache_path}")
