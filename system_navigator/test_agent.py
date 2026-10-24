import pytest
from unittest.mock import patch, MagicMock
from main import extract_bash_script, execute_command, generate_response

def test_extract_bash_script():
    # Test valid extraction
    text = "Here is the command:\n```bash\nls -la\n```\nIt lists files."
    assert extract_bash_script(text) == "ls -la"

    # Test multi-line extraction
    text2 = "Run this:\n```bash\necho 'hello'\nls\n```"
    assert extract_bash_script(text2) == "echo 'hello'\nls"

    # Test no bash block
    text3 = "No bash block here."
    assert extract_bash_script(text3) is None

def test_execute_command():
    # Test successful command
    stdout, stderr, code = execute_command("echo 'test'")
    assert "test" in stdout
    assert code == 0

    # Test failing command
    stdout, stderr, code = execute_command("ls non_existent_file_12345")
    assert code != 0
    assert "No such file or directory" in stderr

@patch('main.requests.post')
def test_generate_response_success(mock_post):
    # Setup mock
    mock_response = MagicMock()
    mock_response.json.return_value = {"response": "test response", "context": [1, 2, 3]}
    mock_response.raise_for_status.return_value = None
    mock_post.return_value = mock_response

    result = generate_response("Hello")

    assert result is not None
    assert result["response"] == "test response"
    assert result["context"] == [1, 2, 3]
    mock_post.assert_called_once()

@patch('main.requests.post')
def test_generate_response_failure(mock_post):
    # Setup mock to raise exception
    import requests
    mock_post.side_effect = requests.exceptions.RequestException("Connection error")

    result = generate_response("Hello")

    assert result is None
    mock_post.assert_called_once()
