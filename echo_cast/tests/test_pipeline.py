import pytest
import os
import json
from unittest.mock import patch
import sys

# Add parent dir to path so we can import pipeline
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pipeline

@pytest.fixture
def mock_template_file(tmp_path):
    template_dir = tmp_path / "templates"
    template_dir.mkdir()
    template_file = template_dir / "player.html"
    template_file.write_text("<html>{{CAST_DATA}} - {{SCRIPT_DATA}}</html>")

    # We need to monkeypatch os.path.dirname in pipeline.py to use tmp_path
    return template_file

@patch('pipeline.requests.post')
def test_run_director(mock_post):
    # Setup mock response
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {
        'message': {
            'content': json.dumps([
                {"name": "Alice", "role": "Host", "pitch": 1.0, "rate": 1.0},
                {"name": "Bob", "role": "Expert", "pitch": 0.8, "rate": 1.2}
            ])
        }
    }

    result = pipeline.run_director("Test text")

    assert len(result) == 2
    assert result[0]["name"] == "Alice"
    assert result[1]["name"] == "Bob"

@patch('pipeline.requests.post')
def test_run_scriptwriter(mock_post):
    # Setup mock response
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {
        'message': {
            'content': json.dumps([
                {"speaker": "Alice", "text": "Hello Bob"},
                {"speaker": "Bob", "text": "Hi Alice"}
            ])
        }
    }

    personas = [{"name": "Alice"}, {"name": "Bob"}]
    result = pipeline.run_scriptwriter("Test text", personas)

    assert len(result) == 2
    assert result[0]["speaker"] == "Alice"
    assert result[0]["text"] == "Hello Bob"

def test_run_producer(tmp_path):
    personas = [{"name": "Alice"}]
    script = [{"speaker": "Alice", "text": "Hello"}]
    out_file = tmp_path / "output.html"

    # We have to mock the template path reading in run_producer
    # since it looks relative to __file__

    # Create a dummy templates dir relative to where tests are run
    # OR we can just patch it.

    with patch('pipeline.os.path.dirname') as mock_dirname:
        # Mock dirname to point to tmp_path so it looks for templates there
        mock_dirname.return_value = str(tmp_path)

        # Create templates dir in tmp_path
        (tmp_path / "templates").mkdir()
        (tmp_path / "templates" / "player.html").write_text("DATA: {{CAST_DATA}} | {{SCRIPT_DATA}}")

        pipeline.run_producer(personas, script, str(out_file))

        assert out_file.exists()
        content = out_file.read_text()
        assert "DATA: [{\"name\": \"Alice\"}] | [{\"speaker\": \"Alice\", \"text\": \"Hello\"}]" in content
