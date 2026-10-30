import logging
from typing import Dict, Any
from actverge.agents.state import ActVergeState
from actverge.executor.evidence import EvidencePackager

logger = logging.getLogger("actverge.evidence_collector")

async def evidence_collector_node(state: ActVergeState) -> Dict[str, Any]:
    """
    Evidence Collector Node.
    Aggregates DOM snapshots, screenshots, traces, and headers into an evidence package.
    """
    logger.info(f"Packaging evidence for task {state['task_id']}")
    packager = EvidencePackager()
    evidence_package = await packager.package_evidence(
        task_id=state["task_id"],
        baseline=state.get("baseline_snapshot"),
        post_state=state.get("post_action_snapshot"),
        trace=state.get("action_trace")
    )
    return {"evidence_package": evidence_package}
