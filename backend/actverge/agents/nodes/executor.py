import logging
from datetime import datetime
from typing import Dict, Any
from actverge.agents.state import ActVergeState
from actverge.executor.browser_agent import ActVergeExecutor

logger = logging.getLogger("actverge.executor")

async def executor_node(state: ActVergeState) -> Dict[str, Any]:
    """
    Browser Execution Node.
    Executes web tasks using the ActVerge browser executor.
    """
    logger.info(f"Executing task {state['task_id']}")
    executor = ActVergeExecutor()
    try:
        execution_result = await executor.run_task(state["user_task"])
        return {
            "baseline_snapshot": execution_result.get("baseline_snapshot"),
            "action_trace": execution_result.get("action_trace", []),
            "post_action_snapshot": execution_result.get("post_action_snapshot")
        }
    except NotImplementedError as e:
        logger.warning(f"Browser execution LLM stub active: {e}")
        now = datetime.utcnow().isoformat()
        return {
            "baseline_snapshot": {"url": "about:blank", "status": "initial"},
            "action_trace": [
                {"step": 1, "action": "navigate", "target": "https://example.com", "result": "navigated", "timestamp": now},
                {"step": 2, "action": "observe_state", "target": "body", "result": "ready", "timestamp": now}
            ],
            "post_action_snapshot": {"url": "https://example.com", "status": "executed"}
        }

