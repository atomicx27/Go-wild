import os
import shutil
import pytest
import responses
from agent import AutonomousCoderSwarm

@pytest.fixture
def agent_setup(tmp_path):
    # Set up temporary base directory
    base_dir = tmp_path / "test_swarm"
    base_dir.mkdir()

    agent = AutonomousCoderSwarm(base_dir=str(base_dir))

    yield agent

    # Cleanup done automatically by pytest's tmp_path fixture,
    # but could be done manually if needed

def test_extract_python_code():
    agent = AutonomousCoderSwarm(base_dir="test_dir")

    # Test with python block
    resp = "Here is the code:\n```python\nprint('hello')\n```"
    assert agent.extract_python_code(resp).strip() == "print('hello')"

    # Test with generic block
    resp = "Here is the code:\n```\nprint('hello')\n```"
    assert agent.extract_python_code(resp).strip() == "print('hello')"

    # Test with no block
    resp = "print('hello')"
    assert agent.extract_python_code(resp).strip() == "print('hello')"

@responses.activate
def test_process_prompt_success(agent_setup):
    agent = agent_setup

    # Create mock prompt
    test_filename = "test_prompt.txt"
    test_file_path = os.path.join(agent.inbox_dir, test_filename)
    with open(test_file_path, "w") as f:
        f.write("Write a script to say hello")

    # Mock Ollama API response
    responses.add(
        responses.POST,
        agent.ollama_url,
        json={"response": "```python\nprint('Hello World')\n```"},
        status=200
    )

    # Process
    agent.process_prompt(test_filename)

    # Assertions
    # 1. File moved to processed
    assert not os.path.exists(test_file_path)
    assert os.path.exists(os.path.join(agent.processed_dir, test_filename))

    # 2. Output script generated
    output_path = os.path.join(agent.scripts_dir, "test_prompt_output.py")
    assert os.path.exists(output_path)

    with open(output_path, "r") as f:
        content = f.read()
    assert content.strip() == "print('Hello World')"

def test_process_prompt_empty(agent_setup):
    agent = agent_setup

    # Create empty prompt
    test_filename = "empty_prompt.txt"
    test_file_path = os.path.join(agent.inbox_dir, test_filename)
    with open(test_file_path, "w") as f:
        f.write("")

    # Process
    agent.process_prompt(test_filename)

    # File should be in rejected
    assert not os.path.exists(test_file_path)
    assert os.path.exists(os.path.join(agent.rejected_dir, test_filename))

@responses.activate
def test_process_prompt_api_error(agent_setup):
    agent = agent_setup

    # Create mock prompt
    test_filename = "error_prompt.txt"
    test_file_path = os.path.join(agent.inbox_dir, test_filename)
    with open(test_file_path, "w") as f:
        f.write("Trigger error")

    # Mock Ollama API failure
    responses.add(
        responses.POST,
        agent.ollama_url,
        json={"error": "Model not found"},
        status=404
    )

    # Process
    agent.process_prompt(test_filename)

    # File should be in rejected
    assert not os.path.exists(test_file_path)
    assert os.path.exists(os.path.join(agent.rejected_dir, test_filename))
