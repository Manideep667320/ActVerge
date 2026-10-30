import logging
from typing import Dict, Any
from actverge.agents.state import ActVergeState
from actverge.executor.observer import StateObserver

logger = logging.getLogger("actverge.state_observer")

async def state_observer_node(state: ActVergeState) -> Dict[str, Any]:
    """
    State Observer Node.
    Captures post-action DOM, accessibility tree, and screenshot.
    Preserves and enriches dynamic post-action snapshot from the executor.
    """
    logger.info(f"Observing state for task {state['task_id']}")
    observer = StateObserver()
    snapshot = await observer.capture_current_state(
        existing_snapshot=state.get("post_action_snapshot"),
        task=state.get("user_task")
    )
    return {"post_action_snapshot": snapshot}
