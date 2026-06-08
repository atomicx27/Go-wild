import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

# Create a mock data directory context before importing main
import json
import os
from pathlib import Path

# Setup mock data
MOCK_DATA_DIR = Path(__file__).parent / "test_data"
MOCK_DATA_DIR.mkdir(exist_ok=True)
MOCK_MODULE = {
    "title": "Test Title",
    "summary": "Test Summary",
    "persona_name": "Test Persona",
    "persona_greeting": "Hello",
    "flashcards": [],
    "quiz": []
}

with open(MOCK_DATA_DIR / "test_module.json", "w") as f:
    json.dump(MOCK_MODULE, f)

from neuro_mentor.main import app
import neuro_mentor.main

# Patch DATA_DIR directly in the imported module for testing
neuro_mentor.main.DATA_DIR = MOCK_DATA_DIR

client = TestClient(app)

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert "Neuro-Mentor" in response.text

def test_get_modules():
    response = client.get("/api/modules")
    assert response.status_code == 200
    data = response.json()
    assert "modules" in data
    assert len(data["modules"]) == 1
    assert data["modules"][0]["title"] == "Test Title"

@patch("neuro_mentor.main.httpx.AsyncClient")
@pytest.mark.asyncio
async def test_chat_with_tutor(mock_client_class):
    # Create custom mock class to properly handle async context manager and coroutines
    class MockResponse:
        def json(self):
            return {"message": {"content": "Mocked Reply"}}
        def raise_for_status(self):
            pass

    class MockClient:
        async def __aenter__(self):
            return self
        async def __aexit__(self, exc_type, exc_val, exc_tb):
            pass
        async def post(self, *args, **kwargs):
            return MockResponse()

    mock_client_class.return_value = MockClient()

    response = client.post(
        "/api/chat",
        json={"module_id": "test_module", "message": "Hi"}
    )

    assert response.status_code == 200
    data = response.json()
    assert "reply" in data

def teardown_module(module):
    # Cleanup test data
    import shutil
    shutil.rmtree(MOCK_DATA_DIR, ignore_errors=True)
