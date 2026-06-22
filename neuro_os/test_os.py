import pytest
from httpx import AsyncClient, ASGITransport
import os
from pathlib import Path
from main import app, agent

@pytest.fixture
def desktop_dir():
    # Make sure the dir exists and is empty
    d_dir = agent.desktop_dir
    d_dir.mkdir(parents=True, exist_ok=True)
    for f in os.listdir(d_dir):
        os.remove(d_dir / f)
    return d_dir

@pytest.mark.asyncio
async def test_read_desktop_empty(desktop_dir):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/fs/desktop")
    assert response.status_code == 200
    assert response.json() == {"files": []}

@pytest.mark.asyncio
async def test_read_desktop_with_file(desktop_dir):
    # create a dummy file
    test_file = desktop_dir / "test.txt"
    test_file.write_text("Hello Cyberpunk!")

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/fs/desktop")
        assert response.status_code == 200
        assert "test.txt" in response.json()["files"]

        # Test read endpoint
        response_read = await ac.get("/api/fs/read/test.txt")
        assert response_read.status_code == 200
        assert response_read.json() == {"content": "Hello Cyberpunk!"}
