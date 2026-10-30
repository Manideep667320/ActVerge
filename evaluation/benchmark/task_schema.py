"""
task_schema.py
==============
Dataclass definitions for benchmark tasks and controlled test cases
used by the ActVerge evaluation harness.
"""

from dataclasses import dataclass, field
from typing import Optional, Literal


@dataclass
class ExpectedOutcome:
    """Structured specification of what a successful task completion looks like."""

    description: str
    """Human-readable description of the expected end-state."""

    required_conditions: list[str]
    """Verifiable conditions that MUST hold for the outcome to be SUCCESS."""

    forbidden_conditions: list[str]
    """Conditions whose presence signals failure (e.g. error banners, wrong page)."""

    evidence_signals: list[str]
    """Page elements / API responses / screenshots to inspect for confirmation."""


@dataclass
class BenchmarkTask:
    """A single evaluation task drawn from Mind2Web or a controlled test suite."""

    task_id: str
    """Unique identifier — matches Mind2Web annotation_id where applicable."""

    goal: str
    """Natural-language description of the task the agent must complete."""

    domain: str
    """High-level web domain (e.g. 'Shopping', 'Travel', 'Finance')."""

    expected_outcome: ExpectedOutcome
    """Structured specification of what success looks like."""

    ground_truth: Literal["SUCCESS", "PARTIAL", "FAILED", "UNCERTAIN"]
    """Human-labelled ground-truth outcome used for metric computation."""

    failure_variant: Optional[str] = None
    """Describes the injected failure mode for controlled tests.
    Examples: 'validation_error', 'timeout', 'stale_element', 'wrong_url'.
    None for standard (non-adversarial) tasks."""

    is_controlled: bool = True
    """True when the task has a deterministic, injected outcome for evaluation.
    False for real Mind2Web tasks where outcome is inferred from annotations."""
