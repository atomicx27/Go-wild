import pytest
from fastapi.testclient import TestClient
import json
from unittest.mock import AsyncMock, patch

import sys
import os
# Add parent directory to path to import main and agent correctly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "Neural Canvas" in response.text

# Custom Async Context Manager mock for httpx.AsyncClient
class MockAsyncClient:
    def __init__(self, *args, **kwargs):
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

    async def post(self, url, json=None, **kwargs):
        class MockResponse:
            def raise_for_status(self):
                pass
            def json(self):
                return {
                    "message": {
                        "content": '{"nodes": [{"id": 1, "label": "Test Node", "color": "#123456"}], "edges": []}'
                    }
                }
        return MockResponse()

@pytest.mark.asyncio
@patch('agent.httpx.AsyncClient', MockAsyncClient)
async def test_chat_endpoint_mocked():
    initial_state = {"nodes": [], "edges": []}
    response = client.post(
        "/api/chat",
        json={"prompt": "Add a test node", "state": initial_state}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "state" in data
    assert len(data["state"]["nodes"]) == 1
    assert data["state"]["nodes"][0]["label"] == "Test Node"

@pytest.mark.asyncio
async def test_chat_endpoint_fallback():
    # Force a connection error to test fallback
    with patch('agent.httpx.AsyncClient.post', side_effect=Exception("Mocked connection error")):
        initial_state = {"nodes": [{"id": 1}], "edges": []}
        response = client.post(
            "/api/chat",
            json={"prompt": "Test fallback", "state": initial_state}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert len(data["state"]["nodes"]) == 2
        assert "Fallback" in data["state"]["nodes"][1]["label"]
