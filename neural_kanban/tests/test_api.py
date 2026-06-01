import pytest
from fastapi.testclient import TestClient
import os

# We need to set the working directory and DB path before importing main
from backend.main import app
from backend import db

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    # Use an in-memory database for testing or a temporary file
    # For simplicity, we just init the normal one (it will create kanban.db in neural_kanban)
    db.init_db()
    yield
    # Cleanup DB after tests if needed, or leave it.
    if os.path.exists(db.DB_PATH):
        os.remove(db.DB_PATH)

def test_create_and_get_ticket():
    response = client.post("/api/tickets", json={
        "title": "Test Ticket",
        "description": "This is a test ticket",
        "status": "TODO"
    })
    assert response.status_code == 200
    ticket_id = response.json()["id"]

    response = client.get("/api/tickets")
    assert response.status_code == 200
    tickets = response.json()
    assert len(tickets) == 1
    assert tickets[0]["id"] == ticket_id
    assert tickets[0]["title"] == "Test Ticket"
    assert tickets[0]["status"] == "TODO"
    assert tickets[0]["ai_processed"] == 0

def test_update_ticket_status():
    response = client.post("/api/tickets", json={
        "title": "Test Ticket",
        "description": "Desc",
        "status": "TODO"
    })
    ticket_id = response.json()["id"]

    response = client.put(f"/api/tickets/{ticket_id}/status", json={"status": "IN PROGRESS"})
    assert response.status_code == 200

    response = client.get("/api/tickets")
    tickets = response.json()
    assert tickets[0]["status"] == "IN PROGRESS"

def test_add_and_get_comments():
    response = client.post("/api/tickets", json={
        "title": "Test Ticket",
        "description": "Desc",
        "status": "TODO"
    })
    ticket_id = response.json()["id"]

    response = client.post(f"/api/tickets/{ticket_id}/comments", json={
        "author": "User",
        "content": "This is a comment"
    })
    assert response.status_code == 200

    response = client.get(f"/api/tickets/{ticket_id}/comments")
    assert response.status_code == 200
    comments = response.json()
    assert len(comments) == 1
    assert comments[0]["author"] == "User"
    assert comments[0]["content"] == "This is a comment"
