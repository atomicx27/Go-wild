import pytest
from fastapi.testclient import TestClient
from app import app
from unittest.mock import patch

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "Web Weaver" in response.text

@patch("app.search_web")
@patch("langchain_ollama.OllamaLLM.invoke")
def test_chat_endpoint(mock_llm_invoke, mock_search_web):
    mock_search_web.return_value = "Mocked search results."
    mock_llm_invoke.return_value = "This is a mocked LLM response based on search results."

    response = client.post("/chat", json={"message": "Test question?"})
    assert response.status_code == 200
    assert response.json() == {"response": "This is a mocked LLM response based on search results."}

    mock_search_web.assert_called_once_with("Test question?")
    assert "Mocked search results." in mock_llm_invoke.call_args[0][0]
