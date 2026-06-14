import pytest
import asyncio
from unittest.mock import patch, MagicMock

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from swarm import MissionLog, queen_agent, drone_agent, execute_mission

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
    def __init__(self, response_data):
        self.response_data = response_data

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

    async def post(self, url, **kwargs):
        return MockResponse(self.response_data)

@pytest.mark.asyncio
async def test_queen_agent():
    mission_log = MissionLog()
    mock_response_data = {
        "message": {
            "content": "[\"Task 1\", \"Task 2\", \"Task 3\"]"
        }
    }

    with patch('httpx.AsyncClient', return_value=MockAsyncClient(mock_response_data)):
        subtasks = await queen_agent("Test prompt", mission_log)

    assert isinstance(subtasks, list)
    assert len(subtasks) == 3
    assert subtasks[0] == "Task 1"

@pytest.mark.asyncio
async def test_drone_agent():
    mission_log = MissionLog()
    mock_response_data = {
        "message": {
            "content": "Drone execution complete."
        }
    }

    with patch('httpx.AsyncClient', return_value=MockAsyncClient(mock_response_data)):
        result = await drone_agent(1, "Task 1", mission_log)

    assert result == "Drone execution complete."

@pytest.mark.asyncio
async def test_execute_mission():
    mission_log = MissionLog()

    async def mock_queen_agent(prompt, ml):
        return ["T1", "T2"]

    async def mock_drone_agent(d_id, task, ml):
        return f"Done {task}"

    with patch('swarm.queen_agent', side_effect=mock_queen_agent):
        with patch('swarm.drone_agent', side_effect=mock_drone_agent):
            await execute_mission("Do things", mission_log)

    # Check that events were logged
    events = []
    while not mission_log.queue.empty():
        events.append(await mission_log.queue.get())

    assert len(events) == 2  # mission_start, mission_complete
    assert events[0]["type"] == "mission_start"
    assert events[1]["type"] == "mission_complete"
    assert "Done T1" in events[1]["data"]["results"]
