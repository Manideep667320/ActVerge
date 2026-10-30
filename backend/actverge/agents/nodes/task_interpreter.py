import json
import logging
from typing import Dict, Any
from actverge.agents.state import ActVergeState
from actverge.llm.router import call_llm, INTERPRETER_ALIAS

logger = logging.getLogger("actverge.task_interpreter")

DEFAULT_OUTCOME_SPEC = {
    "task_description": "",
    "expected_url_pattern": None,
    "required_dom_elements": [],
    "required_text": ["Success", "Confirmed", "Updated", "Complete"],
    "side_effect_risk": "MEDIUM",
    "is_stub": True
}

async def task_interpreter_node(state: ActVergeState) -> Dict[str, Any]:
    """
    Task Interpreter Node.
    Converts raw user task into an expected outcome specification with verifiable conditions
    using OpenRouter (GPT-4o) via LiteLLM, with fallback to rule baseline.
    """
    user_task = state.get("user_task", "")
    logger.info(f"Interpreting task {state['task_id']}: {user_task}")

    system_prompt = (
        "You are the ActVerge Task Interpreter. Your job is to convert a user digital task "
        "into a structured, testable expected-outcome specification. "
        "Return pure valid JSON with these keys:\n"
        "- task_description (str)\n"
        "- expected_url_pattern (str or null)\n"
        "- required_dom_elements (list of selector strings)\n"
        "- required_text (list of strings that confirm task success)\n"
        "- forbidden_text (list of strings indicating errors or failure)\n"
        "- side_effect_risk (LOW | MEDIUM | HIGH | CRITICAL)\n"
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Task: {user_task}"}
    ]

    llm_response = await call_llm(INTERPRETER_ALIAS, messages, temperature=0.1)
    if llm_response:
        try:
            # Clean markdown code blocks if present
            cleaned = llm_response.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            outcome_spec = json.loads(cleaned.strip())
            outcome_spec["is_stub"] = False
            logger.info(f"Task {state['task_id']} successfully interpreted by LLM.")
            return {"outcome_spec": outcome_spec}
        except Exception as e:
            logger.warning(f"Could not parse LLM output as JSON ({e}); using fallback.")

    # Graceful fallback when OPENROUTER_API_KEY is not set or parsing fails
    fallback_spec = dict(DEFAULT_OUTCOME_SPEC)
    fallback_spec["task_description"] = user_task
    return {"outcome_spec": fallback_spec}

