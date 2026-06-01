import pytest
from fastapi.testclient import TestClient
from neuro_clash.app import app

client = TestClient(app)

def test_start_debate():
    response = client.post(
        "/api/debate/start",
        json={"topic": "Should AI govern humanity?"}
    )
    assert response.status_code == 200
    assert response.json() == {
        "message": "Debate initialized",
        "topic": "Should AI govern humanity?"
    }

def test_start_debate_no_topic():
    response = client.post(
        "/api/debate/start",
        json={}
    )
    assert response.status_code == 400
    assert "Topic is required" in response.json()["detail"]

@pytest.mark.asyncio
async def test_debate_turn_fallback():
    # Since Ollama is likely not running in the test environment,
    # we expect the fallback response to trigger.
    response = client.post(
        "/api/debate/turn",
        json={
            "topic": "AI governance",
            "history": [],
            "agent": "Alpha"
        }
    )
    assert response.status_code == 200
    assert "Alpha system offline" in response.json()["response"]
