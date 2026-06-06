import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from ..main import app, init_db

@pytest.fixture(autouse=True)
def setup_db():
    init_db()
    yield

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert b"NEXUS_AUTOMATA" in response.content

def test_list_workflows_empty():
    response = client.get("/api/workflows")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

@patch("nexus_automata.main.httpx.AsyncClient.post")
def test_generate_workflow(mock_post):
    # httpx.AsyncClient.post is mocked to return a context manager-like mock
    # because of `async with httpx.AsyncClient() as client: client.post()`
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "message": {
            "content": '[{"id": "s1", "type": "shell", "content": "echo Hello"}]'
        }
    }
    # Important: make the mock awaitable, and its raise_for_status a regular func
    async def async_post(*args, **kwargs):
        return mock_response
    mock_post.side_effect = async_post

    response = client.post("/api/generate_workflow", json={"goal": "Say hello"})
    assert response.status_code == 200
    data = response.json()
    assert data["goal"] == "Say hello"
    assert len(data["steps"]) == 1
    assert data["steps"][0]["content"] == "echo Hello"

    # Check if saved to DB and visible in list
    response_list = client.get("/api/workflows")
    assert len(response_list.json()) > 0
    assert response_list.json()[0]["goal"] == "Say hello"

def test_trigger_and_poll_run():
    # First generate a workflow
    with patch("nexus_automata.main.httpx.AsyncClient.post") as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "message": {
                "content": '[{"id": "s1", "type": "shell", "content": "echo test"}]'
            }
        }
        async def async_post(*args, **kwargs):
            return mock_response
        mock_post.side_effect = async_post

        gen_res = client.post("/api/generate_workflow", json={"goal": "test run"})
        wf_id = gen_res.json()["id"]

    # Trigger run
    run_res = client.post(f"/api/workflows/{wf_id}/run")
    assert run_res.status_code == 200
    run_id = run_res.json()["run_id"]

    # Poll logs
    log_res = client.get(f"/api/runs/{run_id}/logs")
    assert log_res.status_code == 200
    assert "status" in log_res.json()
    assert "logs" in log_res.json()
