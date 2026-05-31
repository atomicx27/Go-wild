import json
import pytest
from unittest.mock import patch, mock_open
from pathlib import Path

# Adjusting import since we run this from synth_scribe/tests
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from synth_scribe import get_python_files, analyze_codebase, run_agent

def test_get_python_files(tmp_path):
    d = tmp_path / "test_dir"
    d.mkdir()
    f1 = d / "file1.py"
    f1.write_text("print('hello')")
    f2 = d / "file2.txt"
    f2.write_text("hello")
    f3 = d / "file3.py"
    f3.write_text("print('world')")

    files = get_python_files(d)
    assert len(files) == 2
    assert f1 in files
    assert f3 in files
    assert f2 not in files

@patch('synth_scribe.requests.post')
def test_analyze_codebase_success(mock_post):
    mock_response = mock_post.return_value
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "message": {
            "content": '{"summary": "Test summary", "mermaid": "graph TD\\nA-->B"}'
        }
    }

    result = analyze_codebase("def test(): pass")
    assert result["summary"] == "Test summary"
    assert result["mermaid"] == "graph TD\nA-->B"

@patch('synth_scribe.requests.post')
def test_analyze_codebase_failure(mock_post):
    mock_response = mock_post.return_value
    mock_response.raise_for_status.side_effect = Exception("API Error")

    result = analyze_codebase("def test(): pass")
    assert "Failed to generate summary." in result["summary"]
    assert "graph TD\n  A[Error]" in result["mermaid"]

@patch('synth_scribe.analyze_codebase')
@patch('synth_scribe.get_python_files')
def test_run_agent(mock_get_files, mock_analyze, tmp_path):
    # Setup mock files
    f1 = tmp_path / "dummy.py"
    f1.write_text("print('dummy')")
    mock_get_files.return_value = [f1]

    mock_analyze.return_value = {
        "summary": "Mocked Cyberpunk Summary",
        "mermaid": "graph TD\nMOCK-->DATA"
    }

    m_open = mock_open(read_data="<html>{{ SUMMARY }} and {{ MERMAID }}</html>")
    with patch('builtins.open', m_open):
        with patch('synth_scribe.Path.mkdir'):
            with patch('synth_scribe.shutil.copy'):
                run_agent(str(tmp_path))

                # Check if write was called with replaced content
                handle = m_open()
                written_content = "".join(call.args[0] for call in handle.write.mock_calls)
                if written_content:
                    assert "Mocked Cyberpunk Summary" in written_content
                    assert "graph TD\nMOCK-->DATA" in written_content
