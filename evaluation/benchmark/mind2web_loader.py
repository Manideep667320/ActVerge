"""
mind2web_loader.py
==================
Loads Mind2Web task scenarios from the HuggingFace Hub.

Dataset: https://huggingface.co/datasets/osunlp/Mind2Web
Paper  : Deng et al. (2023), NeurIPS 2023.

Usage
-----
    from evaluation.benchmark.mind2web_loader import load_mind2web_tasks

    tasks = load_mind2web_tasks(split="test", max_tasks=50)
    for t in tasks:
        print(t["task_id"], t["goal"])
"""

import os
from typing import Optional
from datasets import load_dataset


def load_mind2web_tasks(
    split: str = "test",
    max_tasks: int = 50,
    streaming: bool = True,
    token: Optional[str] = None
) -> list[dict]:
    """Load Mind2Web task scenarios from HuggingFace on-the-fly.

    Parameters
    ----------
    split : str
        Dataset split to load ("train", "validation", or "test").
    max_tasks : int
        Maximum number of tasks to return. Useful for smoke-tests and evaluations.
    streaming : bool, default=True
        When True, streams samples on-the-fly WITHOUT downloading the entire
        multi-gigabyte dataset to local storage.
    token : str, optional
        Hugging Face access token. If omitted, falls back to HF_TOKEN or HUGGING_FACE_HUB_TOKEN
        environment variables, or cached credentials from `huggingface-cli login`.

    Returns
    -------
    list[dict]
        Each dict contains:
        - task_id        : unique annotation identifier
        - goal           : natural-language task description
        - domain         : high-level web domain (e.g. "Shopping")
        - subdomain      : finer-grained domain category
        - action_sequence: list of recorded human actions
    """
    hf_token = token or os.environ.get("HF_TOKEN") or os.environ.get("HUGGING_FACE_HUB_TOKEN")

    # Load with streaming=True so data is streamed on-demand without full disk download
    dataset = load_dataset(
        "osunlp/Mind2Web",
        split=split,
        streaming=streaming,
        token=hf_token
    )

    tasks: list[dict] = []
    if streaming:
        for item in dataset:
            tasks.append({
                "task_id": item.get("annotation_id"),
                "goal": item.get("confirmed_task"),
                "domain": item.get("domain"),
                "subdomain": item.get("subdomain"),
                "action_sequence": item.get("actions", []),
            })
            if len(tasks) >= max_tasks:
                break
    else:
        for item in dataset.select(range(min(max_tasks, len(dataset)))):
            tasks.append({
                "task_id": item.get("annotation_id"),
                "goal": item.get("confirmed_task"),
                "domain": item.get("domain"),
                "subdomain": item.get("subdomain"),
                "action_sequence": item.get("actions", []),
            })

    return tasks

