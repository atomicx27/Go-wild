import pytest
from fastapi.testclient import TestClient
from main import app, jobs

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "Cyber Oracle" in response.text

def test_create_bounty():
    response = client.post("/api/bounty", json={"query": "Test API"})
    assert response.status_code == 200
    data = response.json()
    assert "job_id" in data

    # Check that job was added to the store
    job_id = data["job_id"]
    assert job_id in jobs

def test_stream_status_not_found():
    response = client.get("/api/stream/invalid_id")
    # SSE starlette streams the response immediately
    # We can read the first line of the stream
    stream_content = b"".join(response.iter_bytes())
    assert b"Job not found" in stream_content
