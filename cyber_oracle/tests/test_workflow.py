import pytest
import asyncio
from unittest.mock import patch, MagicMock
from agents.workflow import run_oracle_workflow

# Mock AsyncClient context manager for testing httpx
class MockAsyncClient:
    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

    async def post(self, url, **kwargs):
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()

        # Determine response based on mocked content in payload
        messages = kwargs.get("json", {}).get("messages", [])
        system_msg = messages[0]["content"].lower() if messages else ""
        last_msg = messages[-1]["content"].lower() if messages else ""

        if "the fixer" in system_msg:
            content = '["Topic A", "Topic B"]'
        elif "netrunner" in system_msg:
            content = "Detailed mock research findings."
        else:
            content = "# Final Dossier\n\nContent here."

        mock_response.json = MagicMock(return_value={"message": {"content": content}})
        return mock_response

@pytest.mark.asyncio
async def test_workflow_execution():
    queue = asyncio.Queue()

    with patch("httpx.AsyncClient", new=MockAsyncClient):
        await run_oracle_workflow("Test Query", queue)

    updates = []
    while not queue.empty():
        updates.append(await queue.get())

    # Check that we received expected statuses
    statuses = [u["status"] for u in updates]
    assert "analyzing" in statuses
    assert "researching" in statuses
    assert "synthesizing" in statuses
    assert "complete" in statuses

    # Check final dossier is present
    final_update = updates[-1]
    assert "dossier" in final_update
    assert "# Final Dossier" in final_update["dossier"]
