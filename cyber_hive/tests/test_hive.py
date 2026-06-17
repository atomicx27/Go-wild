import pytest
import os
import asyncio
from unittest.mock import patch, MagicMock

from cyber_hive.hive_mind import HiveMind

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
    def __init__(self, *args, **kwargs):
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

    async def post(self, url, json):
        return MockResponse({"message": {"content": "MOCKED_RESPONSE"}})


@pytest.fixture
def mock_hive(tmp_path):
    hive = HiveMind()
    # Override directories for safe testing
    hive.inbox_dir = tmp_path / "inbox"
    hive.outbox_dir = tmp_path / "outbox"
    hive.rejected_dir = tmp_path / "rejected"
    os.makedirs(hive.inbox_dir, exist_ok=True)
    os.makedirs(hive.outbox_dir, exist_ok=True)
    os.makedirs(hive.rejected_dir, exist_ok=True)
    return hive

@pytest.mark.asyncio
async def test_process_with_ollama(mock_hive):
    with patch("httpx.AsyncClient", new=MockAsyncClient):
        result = await mock_hive.process_with_ollama("test prompt")
        assert result == "MOCKED_RESPONSE"

@pytest.mark.asyncio
async def test_watch_inbox_processes_file(mock_hive):
    # Setup test file
    test_file = mock_hive.inbox_dir / "test_idea.txt"
    with open(test_file, "w") as f:
        f.write("A cool idea")

    async def mock_process(prompt):
        return f"Processed: {prompt}"

    mock_hive.process_with_ollama = mock_process

    # Run loop for a short time
    task = asyncio.create_task(mock_hive.watch_inbox())
    await asyncio.sleep(0.5)
    mock_hive.running = False
    await task

    # Assertions
    assert not os.path.exists(test_file)
    outbox_files = os.listdir(mock_hive.outbox_dir)
    assert len(outbox_files) == 1
    assert outbox_files[0] == "processed_test_idea.txt"

    with open(mock_hive.outbox_dir / outbox_files[0], "r") as f:
        content = f.read()
    assert content == "Processed: A cool idea"

@pytest.mark.asyncio
async def test_watch_inbox_handles_failure(mock_hive):
    # Setup test file
    test_file = mock_hive.inbox_dir / "bad_idea.txt"
    with open(test_file, "w") as f:
        f.write("A bad idea")

    async def mock_process_fail(prompt):
        raise Exception("Failed to process")

    mock_hive.process_with_ollama = mock_process_fail

    # Run loop for a short time
    task = asyncio.create_task(mock_hive.watch_inbox())
    await asyncio.sleep(0.5)
    mock_hive.running = False
    await task

    # Assertions
    assert not os.path.exists(test_file)
    assert len(os.listdir(mock_hive.outbox_dir)) == 0

    rejected_files = os.listdir(mock_hive.rejected_dir)
    assert len(rejected_files) == 1
    assert rejected_files[0] == "bad_idea.txt"
