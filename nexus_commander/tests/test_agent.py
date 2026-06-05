import pytest
from backend.agent import parse_agent_response

def test_parse_agent_response_think_execute():
    text = """<THINK>I need to list the files in the directory.</THINK>
<EXECUTE>ls -la</EXECUTE>"""

    parsed = parse_agent_response(text)

    assert parsed["think"] == "I need to list the files in the directory."
    assert parsed["execute"] == "ls -la"
    assert parsed["answer"] is None

def test_parse_agent_response_think_answer():
    text = """<THINK>I have found the information.</THINK>
<ANSWER>The largest file is 10MB.</ANSWER>"""

    parsed = parse_agent_response(text)

    assert parsed["think"] == "I have found the information."
    assert parsed["execute"] is None
    assert parsed["answer"] == "The largest file is 10MB."

def test_parse_agent_response_multiline():
    text = """<THINK>
I need to do a few things here.
First, check the directory.
Second, read the file.
</THINK>
<EXECUTE>
cat some_file.txt | grep "something"
</EXECUTE>"""

    parsed = parse_agent_response(text)

    assert parsed["think"] == "I need to do a few things here.\nFirst, check the directory.\nSecond, read the file."
    assert parsed["execute"] == "cat some_file.txt | grep \"something\""
    assert parsed["answer"] is None

def test_parse_agent_response_empty():
    text = "Just some random text without tags."
    parsed = parse_agent_response(text)
    assert parsed["think"] is None
    assert parsed["execute"] is None
    assert parsed["answer"] is None
