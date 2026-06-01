import pytest
import os
import json
from pathlib import Path
from unittest.mock import patch, MagicMock

from cyber_forge.forge import process_idea, initialize, INBOX_DIR, ARMORY_DIR
from cyber_forge.llm_client import extract_code_blocks

def test_extract_code_blocks_specific():
    text = "Here is some code:\n```python\nprint('hello')\n```\nEnjoy!"
    extracted = extract_code_blocks(text, "python")
    assert extracted.strip() == "print('hello')"

def test_extract_code_blocks_generic():
    text = "Here is some code:\n```\nprint('world')\n```\nEnjoy!"
    extracted = extract_code_blocks(text, "python")
    assert extracted.strip() == "print('world')"

def test_extract_code_blocks_fallback():
    text = "def hello():\n    return 'hello'"
    extracted = extract_code_blocks(text, "python")
    assert "def hello():" in extracted

@patch('cyber_forge.forge.chat_with_ollama')
def test_process_idea_success(mock_chat, tmp_path):
    """Test the full loop when generation succeeds and tests pass."""

    # Mock responses for tool code, test code
    mock_chat.side_effect = [
        "```python\ndef add(a, b): return a + b\n```",  # Tool
        "```python\nfrom tool import add\ndef test_add(): assert add(1, 2) == 3\n```"  # Test
    ]

    # Override paths for testing
    import cyber_forge.forge as forge_module
    forge_module.BASE_DIR = tmp_path
    forge_module.INBOX_DIR = tmp_path / "inbox"
    forge_module.ARMORY_DIR = tmp_path / "armory"
    forge_module.initialize()

    # Create test idea
    idea_file = forge_module.INBOX_DIR / "math_adder.txt"
    idea_file.write_text("A simple function to add two numbers.", encoding='utf-8')

    # Run process
    result = process_idea(idea_file)

    assert result is True
    assert not idea_file.exists()  # Should be deleted
    assert (forge_module.ARMORY_DIR / "math_adder.py").exists()
    assert (forge_module.ARMORY_DIR / "test_math_adder.py").exists()
    assert (forge_module.ARMORY_DIR / "math_adder.json").exists()
    assert (forge_module.ARMORY_DIR / "index.html").exists()

@patch('cyber_forge.forge.chat_with_ollama')
def test_process_idea_healing(mock_chat, tmp_path):
    """Test the loop when initial tests fail, and it heals."""

    # Tool: broken, Test: good, Tool Fixed: good, Test Fixed: good
    mock_chat.side_effect = [
        "```python\ndef add(a, b): return a - b\n```",  # Initial broken tool
        "```python\nfrom tool import add\ndef test_add(): assert add(1, 2) == 3\n```", # Test
        # Healing step JSON
        json.dumps({
            "tool_code": "def add(a, b): return a + b",
            "test_code": "from tool import add\ndef test_add(): assert add(1, 2) == 3"
        })
    ]

    import cyber_forge.forge as forge_module
    forge_module.BASE_DIR = tmp_path
    forge_module.INBOX_DIR = tmp_path / "inbox"
    forge_module.ARMORY_DIR = tmp_path / "armory"
    forge_module.initialize()

    idea_file = forge_module.INBOX_DIR / "healing_adder.txt"
    idea_file.write_text("A simple function to add two numbers.", encoding='utf-8')

    result = process_idea(idea_file)

    assert result is True
    assert mock_chat.call_count == 3  # Initial code, initial test, healing step

    meta_file = forge_module.ARMORY_DIR / "healing_adder.json"
    assert meta_file.exists()
    meta = json.loads(meta_file.read_text())
    assert meta["attempts"] == 2 # Initial failed, then healed passed

@patch('cyber_forge.forge.chat_with_ollama')
def test_process_idea_failure(mock_chat, tmp_path):
    """Test when healing fails max attempts."""

    # Always return broken code
    mock_chat.return_value = "```python\nraise Exception('Broken')\n```"

    import cyber_forge.forge as forge_module
    forge_module.BASE_DIR = tmp_path
    forge_module.INBOX_DIR = tmp_path / "inbox"
    forge_module.ARMORY_DIR = tmp_path / "armory"
    forge_module.initialize()

    idea_file = forge_module.INBOX_DIR / "impossible.txt"
    idea_file.write_text("Do the impossible.", encoding='utf-8')

    result = process_idea(idea_file)

    assert result is False
    assert (forge_module.INBOX_DIR / "impossible.failed").exists()
