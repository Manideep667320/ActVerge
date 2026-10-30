from typing import TypedDict, Optional, Literal, Dict, Any, List

VerdictType = Literal["SUCCESS", "PARTIAL", "FAILED", "UNCERTAIN", "PENDING"]

class ActVergeState(TypedDict):
    task_id: str
    user_task: str                               # raw user request
    outcome_spec: Optional[Dict[str, Any]]       # from task interpreter
    baseline_snapshot: Optional[Dict[str, Any]]  # before-action state
    action_trace: Optional[List[Dict[str, Any]]] # browser-use action log
    post_action_snapshot: Optional[Dict[str, Any]]
    evidence_package: Optional[Dict[str, Any]]
    verdict: VerdictType
    verdict_reasoning: Optional[str]
    recovery_attempted: bool
    recovery_safe: bool
    escalated: bool
    error: Optional[str]
    created_at: str
    retry_count: Optional[int]
    recovery_action: Optional[str]
