import os
import sqlite3
import pytest
from unittest.mock import patch, MagicMock

# Make sure tests look for modules in the parent directory
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import main

@pytest.fixture
def temp_db(tmp_path):
    db_path = tmp_path / "test_nexus.db"

    # Override the DB_PATH in main
    original_db = main.DB_PATH
    main.DB_PATH = str(db_path)

    main.setup_db()

    yield db_path

    # Restore original path
    main.DB_PATH = original_db

def test_setup_db(temp_db):
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tasks'")
    table = cursor.fetchone()
    assert table is not None

    cursor.execute("PRAGMA table_info(tasks)")
    columns = {col[1]: col[2] for col in cursor.fetchall()}
    assert 'id' in columns
    assert 'spec_file' in columns
    assert 'filepath' in columns
    assert 'description' in columns
    assert 'status' in columns
    assert 'code' in columns
    assert 'created_at' in columns
    conn.close()

def test_tasks_insertion(temp_db):
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO tasks (spec_file, filepath, description, status) VALUES (?, ?, ?, ?)",
        ("test_spec.txt", "index.html", "HTML File", "TODO")
    )
    conn.commit()

    cursor.execute("SELECT filepath, status FROM tasks")
    row = cursor.fetchone()
    assert row[0] == "index.html"
    assert row[1] == "TODO"
    conn.close()

@patch('main.urllib.request.urlopen')
def test_query_ollama(mock_urlopen):
    # Mock the Ollama response
    mock_response = MagicMock()
    mock_response.read.return_value = b'{"response": "{\\"filepath\\": \\"test.py\\"}"}'
    mock_urlopen.return_value.__enter__.return_value = mock_response

    result = main.query_ollama("Test prompt")

    assert 'filepath' in result
    assert result == '{"filepath": "test.py"}'
