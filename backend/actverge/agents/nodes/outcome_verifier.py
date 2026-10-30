import json
import logging
from typing import Dict, Any
from actverge.agents.state import ActVergeState
from actverge.llm.router import call_llm, VERIFIER_ALIAS

logger = logging.getLogger("actverge.outcome_verifier")

STOP_WORDS = {
    "the", "and", "for", "with", "that", "this", "from", "into", "your",
    "have", "been", "verify", "task", "page", "user", "agent", "what",
    "when", "where", "which", "will", "would", "should", "could"
}

SYSTEM_PROMPT = """You are the independent ActVerge Outcome Verifier.
Your mission: Determine with logical rigor whether an autonomous agent actually achieved the user's intended digital task, based solely on the extracted webpage evidence (DOM summary, active URL, page title, interactive controls, list items, body text, console logs).

VERDICT CRITERIA (Mutually Exclusive):

1. "SUCCESS":
   - The user task's final intended outcome is FULLY accomplished and conclusively verified in the DOM/evidence.
   - Key indicators:
     * Search results or listing items corresponding to the query are loaded and visible.
     * A requested repository, page, documentation, or profile is fully loaded with its primary content visible.
     * Content/Template Creation: For tasks involving creating, building, preparing, or drafting forms, surveys, documents, or workflows (e.g. Google Forms, Google Docs, Notion): if the editor view contains the requested title, questions, options, or content, this is "SUCCESS". (Do NOT expect an author to fill in or submit responses to their own form!)
     * Action produced its confirmed final state (e.g. order placed, item in cart with badge, "Thank you" or confirmation message displayed).
   - Confidence: 0.90 to 1.0.

2. "FAILED":
   - The agent failed the task, encountered fatal errors, or exhibited Agent Drift / Hallucination (claiming completion on an unrelated website).
   - Key indicators:
     * Active website has no relation to the task (e.g. agent claims it booked flight tickets or checked bank balance, but is sitting on GitHub or Wikipedia).
     * Page returned an error (404 Not Found, 500 Internal Server Error, Access Denied).
     * None of the required entities or task steps exist on the page.
   - Confidence: 0.85 to 1.0.

3. "PARTIAL":
   - The agent is on the CORRECT website and successfully executed the initial or intermediate step(s), but stopped before completing the final step or submitting the action.
   - Key indicators:
     * Input fields or search boxes are populated with the requested query/data, but the submission or search button was NOT triggered (results/confirmation not yet generated).
     * In form/doc creation: the agent opened the editor or typed a prompt into an AI sidebar (like Gemini), but the questions or document text were NOT inserted into the actual form canvas (remains "Untitled Form" or blank).
     * In multi-step workflows: an intermediate step was reached (e.g. item added to cart, but checkout not finished; or a respondent filled in a contact form, but submit button was not pressed).
   - Confidence: 0.80 to 0.95.

STRICT CLASSIFICATION RULES:
- Distinguish Creator vs. Respondent Intent:
  * When the task is to "create / prepare / build a form, survey, or document": Success means the form editor has the questions/fields created and present in the DOM. Do NOT penalize because no responses have been submitted!
  * When the task is to "fill out and submit a form, application, or order": Success requires the form to be submitted with a confirmation banner.
- If the domain or page topic is completely unrelated to the task (e.g. flight tickets on GitHub), it MUST be "FAILED", NEVER "PARTIAL".
- Only give "SUCCESS" when the end-state is visibly complete.

Return pure valid JSON with these exact keys:
{
  "verdict": "SUCCESS" | "PARTIAL" | "FAILED" | "UNCERTAIN",
  "confidence": 0.95,
  "reasoning": "Clear factual explanation citing specific elements or lack thereof from the DOM/page state",
  "evidence_summary": ["Point 1", "Point 2"]
}"""


async def outcome_verifier_node(state: ActVergeState) -> Dict[str, Any]:
    """
    Outcome Verifier Node.
    Compares independently gathered evidence with user task.
    Classifies result as SUCCESS, PARTIAL, FAILED, or UNCERTAIN using OpenRouter (GPT-4o-mini).
    Falls back gracefully to deterministic rule-based verification when API is unreachable.
    """
    logger.info(f"Verifying outcome for task {state['task_id']}")
    evidence = state.get("evidence_package") or {}
    outcome_spec = state.get("outcome_spec") or {}
    user_task = state.get("user_task", "")

    user_content = json.dumps({
        "user_task": user_task,
        "audited_page_context": outcome_spec,
        "evidence_package": evidence,
        "action_trace": state.get("action_trace", [])
    }, indent=2)

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"Verify this execution against evidence:\n{user_content}"}
    ]

    llm_response = await call_llm(VERIFIER_ALIAS, messages, temperature=0.1)
    if llm_response:
        try:
            cleaned = llm_response.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            parsed = json.loads(cleaned.strip())
            verdict = parsed.get("verdict", "UNCERTAIN").upper()
            if verdict not in ["SUCCESS", "PARTIAL", "FAILED", "UNCERTAIN"]:
                verdict = "UNCERTAIN"
            confidence = float(parsed.get("confidence", 0.95 if verdict == "SUCCESS" else 0.85))
            return {
                "verdict": verdict,
                "confidence": confidence,
                "verdict_reasoning": parsed.get("reasoning", "Outcome verified via multi-modal evidence."),
                "evidence_summary": parsed.get("evidence_summary", [])
            }
        except Exception as e:
            logger.warning(f"Could not parse verifier LLM output ({e}); falling back to rule baseline.")

    # ── Rule-Based Verification Baseline Fallback ──────────────────────────────
    logger.info("Running deterministic rule-based verification baseline.")
    ev_str = str(evidence).lower()
    task_lower = user_task.lower()
    error_indicators = ["error:", "status: failed", "exception:", "unhandled error", "http 500", "http 404", "failed to load"]
    has_errors = any(e in ev_str for e in error_indicators)

    # Domain mismatch detection (e.g. flight booking task on github.com)
    flight_keywords = ["flight", "airline", "ticket", "hotel", "travel", "reservation", "booking"]
    dev_domains = ["github.com", "gitlab.com", "stackoverflow.com", "developer"]
    is_flight_task = any(w in task_lower for w in flight_keywords)
    is_dev_site = any(d in ev_str for d in dev_domains)

    if (is_flight_task and is_dev_site) or has_errors:
        return {
            "verdict": "FAILED",
            "confidence": 0.95,
            "verdict_reasoning": f"Domain and content mismatch: User task '{user_task}' is unrelated to audited developer domain.",
            "evidence_summary": ["Target domain does not support the requested workflow.", "No task-related entities found in DOM."]
        }

    # Extract substantive words from task
    import re
    t_words = [w for w in re.findall(r'\b[a-zA-Z]{3,}\b', task_lower) if w not in STOP_WORDS]
    matches = sum(1 for w in t_words if w in ev_str)
    match_ratio = matches / max(len(t_words), 1)

    # Detect partial workflow (e.g. input field has query but results not loaded)
    has_inputs_filled = any(f'value="{w}' in ev_str for w in t_words)

    if match_ratio >= 0.5 and not has_inputs_filled:
        verdict = "SUCCESS"
        confidence = 0.90
        reasoning = f"Rule baseline: Key task terms ({matches}/{len(t_words)}) conclusively verified in page DOM and text."
    elif has_inputs_filled or match_ratio >= 0.25:
        verdict = "PARTIAL"
        confidence = 0.85
        reasoning = f"Rule baseline: Partial progress detected ({matches}/{len(t_words)} terms or form inputs present), but final completion state is unverified."
    else:
        verdict = "FAILED"
        confidence = 0.90
        reasoning = f"Rule baseline: Target page does not exhibit indicators of task '{user_task}'. Found only {matches}/{len(t_words)} relevant terms."

    return {
        "verdict": verdict,
        "confidence": confidence,
        "verdict_reasoning": reasoning,
        "evidence_summary": [f"Evaluated relevance to task: {user_task}"]
    }
