import pytest
from pathlib import Path
import sys
import os

# Ensure the module can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from chaos_engine import ChaosEngine

@pytest.fixture
def mock_chaos_engine(monkeypatch):
    engine = ChaosEngine()

    # Mock network calls to avoid hitting Ollama during deterministic tests
    def mock_call_ollama(messages, temperature):
        # We need to distinguish between mutation and test generation based on system prompt
        system_prompt = messages[0]['content'].lower()
        content = messages[1]['content'] if len(messages) > 1 else ""

        if "exactly one subtle logic bug" in system_prompt:
            # Inject a simple bug: change return a + b to a - b
            if "def add(" in content:
                return "```python\ndef add(a, b):\n    return a - b\n```"
            return content # fallback
        else:
            # We are generating a test to catch the bug
            return "```python\ndef test_add_edge_case():\n    assert add(2, 2) == 4\n```"

    monkeypatch.setattr(engine, '_call_ollama', mock_call_ollama)
    monkeypatch.setattr(engine, 'test_connection', lambda: True)
    return engine

def test_mutate_file_logic(mock_chaos_engine, tmp_path):
    target_file = tmp_path / "math_funcs.py"
    target_file.write_text("def add(a, b):\n    return a + b\n")

    orig, mut = mock_chaos_engine.mutate_file(target_file)
    assert "return a + b" in orig
    assert "return a - b" in mut

def test_process_target_full_flow(mock_chaos_engine, tmp_path):
    # Setup files
    target_file = tmp_path / "math_funcs.py"
    target_file.write_text("def add(a, b):\n    return a + b\n")

    test_file = tmp_path / "test_math.py"
    test_code = (
        "from math_funcs import add\n"
        "def test_add_zero():\n"
        "    assert add(0, 0) == 0\n" # Weak test, a-b also passes 0,0
    )
    test_file.write_text(test_code)

    # Run the main chaos loop
    # We must ensure pytest runs in the tmp directory so it finds the local math_funcs.py
    # We can mock subprocess.run for safety, but since we are running a real pytest,
    # let's modify run_tests to run in the target dir

    original_run_tests = mock_chaos_engine.run_tests
    def patched_run_tests(filepath):
        import subprocess
        try:
             result = subprocess.run(
                ["pytest", str(filepath)],
                cwd=str(filepath.parent), # RUN IN TMP_PATH
                capture_output=True,
                text=True,
                timeout=30
             )
             return result.returncode == 0
        except Exception:
             return False

    mock_chaos_engine.run_tests = patched_run_tests

    results = mock_chaos_engine.process_target(target_file, test_file)

    assert results["initial_tests_passed"] == True
    assert results["mutation_survived"] == True
    assert results["new_test_generated"] == True
    assert results["new_test_passed"] == True

    # Verify the test file now contains the new test
    final_test_content = test_file.read_text()
    assert "def test_add_edge_case():" in final_test_content

    # Verify the target file was restored
    final_target_content = target_file.read_text()
    assert "return a + b" in final_target_content
