import pytest
from httpx import AsyncClient
from unittest.mock import patch, AsyncMock

@pytest.mark.asyncio
async def test_verify_external_state_api(client: AsyncClient):
    payload = {
        "user_task": "Explore GitHub repositories and open source software",
        "target_url": "https://github.com",
        "page_title": "GitHub",
        "dom_summary": "<main data-url='https://github.com'><title>GitHub</title><p>Explore open source repositories, packages, and code</p></main>"
    }
    
    mock_verifier_response = {
        "verdict": "SUCCESS",
        "confidence": 0.95,
        "verdict_reasoning": "GitHub repository platform verified in DOM.",
        "evidence_summary": ["URL and title match GitHub"]
    }

    with patch("actverge.api.routes.tasks.outcome_verifier_node", new_callable=AsyncMock) as mock_node:
        mock_node.return_value = mock_verifier_response
        response = await client.post("/api/tasks/verify", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "task_id" in data
        assert data["verdict"] == "SUCCESS"
        assert data["confidence"] == 0.95
        assert "reasoning" in data
        assert "evidence_types" in data

@pytest.mark.asyncio
async def test_tasks_crud_api(client: AsyncClient):
    # 1. Create a task via API
    create_payload = {"user_task": "Automated workflow test"}
    with patch("actverge.api.routes.tasks.run_task_job"):
        create_res = await client.post("/api/tasks", json=create_payload)
        assert create_res.status_code == 200
        task_data = create_res.json()
        assert "id" in task_data
        task_id = task_data["id"]
        assert task_data["user_task"] == "Automated workflow test"
        assert task_data["status"] == "queued"

    # 2. List tasks
    list_res = await client.get("/api/tasks")
    assert list_res.status_code == 200
    list_data = list_res.json()
    assert "tasks" in list_data
    assert list_data["total"] >= 1

    # 3. Retrieve single task
    get_res = await client.get(f"/api/tasks/{task_id}")
    assert get_res.status_code == 200
    single_data = get_res.json()
    assert single_data["id"] == task_id

    # 4. Get verdict (pending placeholder)
    verdict_res = await client.get(f"/api/tasks/{task_id}/verdict")
    assert verdict_res.status_code == 200
    verdict_data = verdict_res.json()
    assert verdict_data["task_id"] == task_id
