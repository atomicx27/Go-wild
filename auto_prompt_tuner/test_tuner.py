import pytest
from unittest.mock import patch, MagicMock
from tuner import AutoPromptTuner

@pytest.fixture
def tuner():
    return AutoPromptTuner()

def test_evaluate_prompt_all_pass(tuner):
    test_cases = [
        {"input": "Hi", "expected_output": "Bonjour"},
        {"input": "Bye", "expected_output": "Au revoir"}
    ]

    with patch.object(tuner, 'call_ollama', side_effect=["Voici la traduction: Bonjour", "La traduction est Au Revoir"]) as mock_call:
        score = tuner.evaluate_prompt("Translate:", test_cases)
        assert score == 1.0
        assert mock_call.call_count == 2

def test_evaluate_prompt_partial_pass(tuner):
    test_cases = [
        {"input": "Hi", "expected_output": "Bonjour"},
        {"input": "Bye", "expected_output": "Au revoir"}
    ]

    with patch.object(tuner, 'call_ollama', side_effect=["Voici la traduction: Bonjour", "Goodbye in french is Adios"]) as mock_call:
        score = tuner.evaluate_prompt("Translate:", test_cases)
        assert score == 0.5

def test_mutate_prompt_parsing(tuner):
    mock_response = "Prompt 1---PROMPT_SEPARATOR---Prompt 2---PROMPT_SEPARATOR---Prompt 3"

    with patch.object(tuner, 'call_ollama', return_value=mock_response):
        mutations = tuner.mutate_prompt("old prompt", [{"input": "a", "expected_output": "b", "actual_output": "c"}])
        assert len(mutations) == 3
        assert mutations[0] == "Prompt 1"
        assert mutations[1] == "Prompt 2"
        assert mutations[2] == "Prompt 3"

def test_mutate_prompt_fallback_parsing(tuner):
    mock_response = "1. First prompt\n2. Second prompt\n3. Third prompt"

    with patch.object(tuner, 'call_ollama', return_value=mock_response):
        mutations = tuner.mutate_prompt("old prompt", [{"input": "a", "expected_output": "b", "actual_output": "c"}])
        assert len(mutations) == 3
        assert "First prompt" in mutations[0]
        assert "Second prompt" in mutations[1]
        assert "Third prompt" in mutations[2]
