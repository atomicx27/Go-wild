import pytest
import json
from unittest.mock import patch, MagicMock

# Need to append the parent directory so we can import agent
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent import generate_completion, QueenAgent, WorkerAgent

class MockResponse:
    def __init__(self, json_data, status_code=200):
        self._json_data = json_data
        self.status_code = status_code

    def json(self):
        return self._json_data

    def raise_for_status(self):
        if self.status_code >= 400:
            raise Exception("HTTP Error")

class MockAsyncClient:
    def __init__(self, mock_response_data):
        self.mock_response_data = mock_response_data

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

    async def post(self, url, json=None):
        return MockResponse(self.mock_response_data)

@pytest.mark.asyncio
async def test_generate_completion():
    mock_data = {"message": {"content": "Hello from mock"}}
    with patch("httpx.AsyncClient", return_value=MockAsyncClient(mock_data)):
        result = await generate_completion([{"role": "user", "content": "hi"}])
        assert result == "Hello from mock"

@pytest.mark.asyncio
async def test_queen_agent_breakdown():
    mock_tasks = '["Task 1", "Task 2"]'
    mock_data = {"message": {"content": mock_tasks}}

    queen = QueenAgent()
    with patch("httpx.AsyncClient", return_value=MockAsyncClient(mock_data)):
        tasks = await queen.breakdown_objective("Do something")
        assert len(tasks) == 2
        assert tasks[0] == "Task 1"
        assert tasks[1] == "Task 2"

@pytest.mark.asyncio
async def test_worker_agent_execute():
    mock_data = {"message": {"content": "Task completed successfully."}}

    worker = WorkerAgent()
    with patch("httpx.AsyncClient", return_value=MockAsyncClient(mock_data)):
        result = await worker.execute_task("Do Task 1")
        assert result == "Task completed successfully."
