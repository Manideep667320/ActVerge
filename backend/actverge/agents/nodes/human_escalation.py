import logging
from typing import Dict, Any
from actverge.agents.state import ActVergeState

logger = logging.getLogger("actverge.human_escalation")

async def human_escalation_node(state: ActVergeState) -> Dict[str, Any]:
    """
    Human Escalation Node.
    Flags uncertain or high-risk outcomes for human review.
    """
    logger.info(f"Escalating task {state['task_id']} to human operator.")
    return {
        "escalated": True,
        "verdict_reasoning": (state.get("verdict_reasoning") or "") + " [ESCALATED TO HUMAN FOR VERIFICATION]"
    }
