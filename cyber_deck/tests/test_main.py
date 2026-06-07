import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from cyber_deck.main import app
import json

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert b"Cyber Deck OS" in response.content

def test_static_files():
    response = client.get("/static/css/style.css")
    assert response.status_code == 200
    assert "text/css" in response.headers["content-type"]
    assert b"scanlines" in response.content

@pytest.mark.asyncio
async def test_chat_endpoint_mocked():
    # Because we use httpx stream which is complex to mock purely via standard patch
    # in TestClient context, we will write a specialized test.
    # However, to avoid complexity in this test_weaver context, we can just ensure the endpoint is reachable
    # and returns our mocked error/response.

    # Actually, we can just test the error handling if Ollama is offline
    with patch("cyber_deck.main.httpx.AsyncClient") as mock_client_class:
        class MockClient:
            async def __aenter__(self):
                return self
            async def __aexit__(self, exc_type, exc_val, exc_tb):
                pass
            def stream(self, *args, **kwargs):
                raise Exception("Mocked connection error")

        mock_client_class.return_value = MockClient()

        response = client.post("/api/chat", json={"messages": [{"role": "user", "content": "hello"}]})
        assert response.status_code == 200

        # Read the stream output
        content = response.content.decode('utf-8').strip()
        assert "Mocked connection error" in content

@pytest.mark.asyncio
async def test_forge_endpoint_mocked():
    with patch("cyber_deck.main.httpx.AsyncClient") as mock_client_class:
        class MockClient:
            async def __aenter__(self):
                return self
            async def __aexit__(self, exc_type, exc_val, exc_tb):
                pass
            def stream(self, *args, **kwargs):
                raise Exception("Mocked forge error")

        mock_client_class.return_value = MockClient()

        response = client.post("/api/forge", json={"prompt": "make a test app"})
        assert response.status_code == 200

        content = response.content.decode('utf-8').strip()
        assert "Mocked forge error" in content
