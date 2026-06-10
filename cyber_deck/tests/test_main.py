import pytest
from fastapi.testclient import TestClient
import os
import shutil
from unittest.mock import patch, AsyncMock
from cyber_deck.main import app, WIDGETS_DIR

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_and_teardown():
    # Setup: ensure widgets dir is clean
    if os.path.exists(WIDGETS_DIR):
        for f in os.listdir(WIDGETS_DIR):
            if f.endswith(".html"):
                os.remove(os.path.join(WIDGETS_DIR, f))
    else:
        os.makedirs(WIDGETS_DIR, exist_ok=True)
    yield
    # Teardown: clean up
    if os.path.exists(WIDGETS_DIR):
        for f in os.listdir(WIDGETS_DIR):
            if f.endswith(".html"):
                os.remove(os.path.join(WIDGETS_DIR, f))

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "CyberDeck OS" in response.text

def test_get_widgets_empty():
    response = client.get("/api/widgets")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["widgets"] == []

class MockResponse:
    def __init__(self, json_data, status_code):
        self._json_data = json_data
        self.status_code = status_code

    def json(self):
        return self._json_data

    def raise_for_status(self):
        if self.status_code >= 400:
            raise Exception("HTTP Error")

class MockAsyncContextManager:
    def __init__(self, response):
        self.response = response

    async def __aenter__(self):
        class MockClient:
            def __init__(self, response):
                self.response = response
            async def post(self, *args, **kwargs):
                return self.response
        return MockClient(self.response)

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

@pytest.mark.asyncio
@patch("httpx.AsyncClient")
async def test_execute_command_widget_creation(mock_async_client):
    mock_response_data = {
        "message": {
            "content": '{"type": "widget_creation", "name": "Test Widget", "html": "<div>Test</div>", "message": "Created"}'
        }
    }

    mock_async_client.return_value = MockAsyncContextManager(MockResponse(mock_response_data, 200))

    response = client.post("/api/execute", json={"command": "create test widget"})

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["response"]["type"] == "widget_creation"
    assert data["response"]["name"] == "Test Widget"

    # Verify file was created
    assert os.path.exists(os.path.join(WIDGETS_DIR, "test_widget.html"))
    with open(os.path.join(WIDGETS_DIR, "test_widget.html"), "r") as f:
        assert f.read() == "<div>Test</div>"

@pytest.mark.asyncio
@patch("httpx.AsyncClient")
async def test_execute_command_chat(mock_async_client):
    mock_response_data = {
        "message": {
            "content": '{"type": "chat", "message": "Hello there."}'
        }
    }

    mock_async_client.return_value = MockAsyncContextManager(MockResponse(mock_response_data, 200))

    response = client.post("/api/execute", json={"command": "hello"})

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["response"]["type"] == "chat"
    assert data["response"]["message"] == "Hello there."
