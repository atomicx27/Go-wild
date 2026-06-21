import pytest
from agent import OllamaAgent

def test_extract_code_python_block():
    agent = OllamaAgent()
    text = "Here is the code:\n```python\nprint('Hello')\n```\nDone."
    assert agent.extract_code(text) == "print('Hello')"

def test_extract_code_generic_block():
    agent = OllamaAgent()
    text = "```\nx = 1\n```"
    assert agent.extract_code(text) == "x = 1"

def test_extract_code_no_block():
    agent = OllamaAgent()
    text = "y = 2"
    assert agent.extract_code(text) == "y = 2"
