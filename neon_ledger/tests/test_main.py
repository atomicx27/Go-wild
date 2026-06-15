import pytest
import os
import json
import sqlite3
from fastapi.testclient import TestClient
from unittest.mock import patch

from neon_ledger.main import app
from neon_ledger.database import init_db, get_connection
from neon_ledger.agent import INBOX_DIR, PROCESSED_DIR, agent_loop, process_file, analyze_with_ollama, save_results

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_teardown():
    # Setup
    init_db()
    # Clear tables for clean test
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM transactions")
    cursor.execute("DELETE FROM reports")
    conn.commit()
    conn.close()

    # Ensure dirs exist
    os.makedirs(INBOX_DIR, exist_ok=True)
    os.makedirs(PROCESSED_DIR, exist_ok=True)

    yield

    # Teardown
    for f in os.listdir(INBOX_DIR):
        if f != '.gitkeep':
            os.remove(os.path.join(INBOX_DIR, f))
    for f in os.listdir(PROCESSED_DIR):
        if f != '.gitkeep':
            os.remove(os.path.join(PROCESSED_DIR, f))

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert b"NEON LEDGER" in response.content

@patch('neon_ledger.agent.httpx.post')
def test_agent_processing(mock_post):
    # Mock Ollama Response
    mock_response = mock_post.return_value
    mock_response.status_code = 200

    mock_json_response = {
        "categories": ["Food", "Entertainment"],
        "report": "<p>You are spending too much.</p>"
    }

    mock_response.json.return_value = {
        "response": json.dumps(mock_json_response)
    }

    # Create dummy CSV
    csv_path = os.path.join(INBOX_DIR, "test.csv")
    with open(csv_path, "w") as f:
        f.write("date,description,amount\n")
        f.write("2024-01-01,Burger,-10.50\n")
        f.write("2024-01-02,Movie,-15.00\n")

    # Manually trigger processing functions to avoid infinite loop in test
    result = process_file(csv_path)
    assert result is not None

    csv_string, df = result
    analysis = analyze_with_ollama(csv_string)

    assert analysis is not None
    assert "categories" in analysis

    save_results(df, analysis)

    # Test the API endpoint after data is saved
    api_response = client.get("/api/data")
    assert api_response.status_code == 200

    data = api_response.json()
    assert "<p>You are spending too much.</p>" in data["report"]
    assert len(data["transactions"]) == 2

    categories = data["categories"]
    assert categories.get("Food", 0) == -10.5
    assert categories.get("Entertainment", 0) == -15.0
