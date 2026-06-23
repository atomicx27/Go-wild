import pytest
from httpx import AsyncClient, ASGITransport
from main import app

@pytest.mark.asyncio
async def test_read_main():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/")
    assert response.status_code == 200
    assert "Autonomous AI Research Agent" in response.text

@pytest.mark.asyncio
async def test_research_endpoint():
    # We won't test the actual ollama/wiki API in unit test, just that it returns an SSE stream properly.
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Since it streams, we'll read a bit of it
        async with ac.stream("GET", "/api/research?topic=Test") as response:
            assert response.status_code == 200
            assert "text/event-stream" in response.headers["content-type"]

            # Read the first chunk to ensure it yields correctly
            chunks = []
            async for chunk in response.aiter_bytes():
                chunks.append(chunk.decode())
                if len(chunks) > 0:
                    break

            combined = "".join(chunks)
            assert "data:" in combined
            assert "Test" in combined
