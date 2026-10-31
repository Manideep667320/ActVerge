import pytest
from unittest.mock import patch, AsyncMock
from actverge.agents.nodes.outcome_verifier import outcome_verifier_node

@pytest.mark.asyncio
async def test_verifier_rule_baseline_fallback():
    with patch("actverge.agents.nodes.outcome_verifier.call_llm", new_callable=AsyncMock) as mock_llm:
        mock_llm.return_value = None

        # 1. Test Mismatched Task -> FAILED
        mismatched_state = {
            "task_id": "test-mismatch",
            "user_task": "Book a one-way flight from New York to Tokyo",
            "outcome_spec": {"audited_url": "https://github.com", "audited_page_title": "GitHub"},
            "evidence_package": {
                "dom_summary": "<main data-url='https://github.com'><title>GitHub</title><p>Where software is built</p></main>",
                "screenshot_url": None,
                "console_logs": [],
                "network_logs": [],
                "accessibility_tree": {"role": "WebArea", "name": "GitHub"}
            },
            "action_trace": []
        }
        res_fail = await outcome_verifier_node(mismatched_state)
        assert res_fail["verdict"] == "FAILED"
        assert res_fail["confidence"] >= 0.85

        # 2. Test Matching Task -> SUCCESS
        matching_state = {
            "task_id": "test-match",
            "user_task": "Explore GitHub developer platform repositories and pull requests",
            "outcome_spec": {"audited_url": "https://github.com", "audited_page_title": "GitHub"},
            "evidence_package": {
                "dom_summary": "<main data-url='https://github.com'><title>GitHub</title><p>Explore open source repositories, developer tools, packages, and pull requests.</p></main>",
                "screenshot_url": None,
                "console_logs": [],
                "network_logs": [],
                "accessibility_tree": {"role": "WebArea", "name": "GitHub"}
            },
            "action_trace": []
        }
        res_succ = await outcome_verifier_node(matching_state)
        assert res_succ["verdict"] == "SUCCESS"
        assert res_succ["confidence"] >= 0.80

        # 3. Test Incomplete / Unsubmitted Query -> PARTIAL
        partial_state = {
            "task_id": "test-partial",
            "user_task": "Search for mechanical keyboards under $100 and display listings",
            "outcome_spec": {"audited_url": "https://www.google.com", "audited_page_title": "Google"},
            "evidence_package": {
                "dom_summary": "<main data-url='https://www.google.com'><input type='text' name='q' value='mechanical keyboards under $100'/></main>",
                "screenshot_url": None,
                "console_logs": [],
                "network_logs": [],
                "accessibility_tree": {"role": "WebArea", "name": "Google"}
            },
            "action_trace": []
        }
        res_partial = await outcome_verifier_node(partial_state)
        assert res_partial["verdict"] == "PARTIAL"
        assert res_partial["confidence"] >= 0.75

@pytest.mark.asyncio
async def test_verifier_llm_json_parsing():
    mock_llm_json = """```json
    {
        "verdict": "SUCCESS",
        "confidence": 0.98,
        "reasoning": "The Playwright Python installation command is confirmed in the DOM.",
        "evidence_summary": ["Installation element found in DOM"]
    }
    ```"""
    with patch("actverge.agents.nodes.outcome_verifier.call_llm", new_callable=AsyncMock) as mock_llm:
        mock_llm.return_value = mock_llm_json
        state = {
            "task_id": "test-llm-parse",
            "user_task": "Find installation command for Playwright Python",
            "outcome_spec": {"audited_url": "https://playwright.dev", "audited_page_title": "Playwright"},
            "evidence_package": {
                "dom_summary": "<main><p>pip install pytest-playwright</p></main>"
            },
            "action_trace": []
        }
        res = await outcome_verifier_node(state)
        assert res["verdict"] == "SUCCESS"
        assert res["confidence"] == 0.98
        assert "Playwright" in res["verdict_reasoning"]
