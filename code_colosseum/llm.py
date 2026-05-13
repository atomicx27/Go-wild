import urllib.request
import json

OLLAMA_URL = "http://localhost:11434/api/generate"

def is_ollama_alive():
    """Checks if Ollama is accessible."""
    try:
        req = urllib.request.Request("http://localhost:11434/api/tags", method="GET")
        with urllib.request.urlopen(req, timeout=1) as response:
            return response.status == 200
    except Exception:
        return False

def generate_text(prompt, system_prompt, model="mistral", context=None):
    """
    Calls the Ollama API to generate text.
    Falls back to a mock response if Ollama is unreachable.
    """
    if not is_ollama_alive():
        print(f"[WARN] Ollama unreachable. Using mock response for model '{model}'.")
        return get_mock_response(prompt, system_prompt)

    data = {
        "model": model,
        "prompt": prompt,
        "system": system_prompt,
        "stream": False,
        "options": {
            "temperature": 0.7
        }
    }

    if context:
        data["context"] = context

    req = urllib.request.Request(
        OLLAMA_URL,
        data=json.dumps(data).encode('utf-8'),
        headers={'Content-Type': 'application/json'}
    )

    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            return result.get('response', '')
    except Exception as e:
        print(f"[ERROR] Failed to query Ollama: {e}")
        return get_mock_response(prompt, system_prompt)

def extract_code(text):
    """Extracts code blocks from the generated text."""
    if "```python" in text:
        parts = text.split("```python")
        if len(parts) > 1:
            code_part = parts[1].split("```")[0]
            return code_part.strip()
    if "```" in text:
        parts = text.split("```")
        if len(parts) > 1:
            return parts[1].strip()
    return text.strip()

def get_mock_response(prompt, system_prompt):
    """Provides mock responses for testing without an active Ollama instance."""
    prompt_lower = prompt.lower()

    # Mock for Caesar (Judging)
    if "judge" in system_prompt.lower() or "caesar" in system_prompt.lower():
        return """
        <html>
        <head><title>Battle Report</title></head>
        <body>
        <h1>Colosseum Battle Report</h1>
        <p>It was a fierce battle! Both gladiators fought valiantly.</p>
        <h2>Winner: Spartacus!</h2>
        <p>Spartacus's code was brutally efficient and passed all tests.</p>
        </body>
        </html>
        """

    # Mock for testing
    if "test" in prompt_lower or "pytest" in prompt_lower:
        if "crixus" in system_prompt.lower():
            # Crixus writes tests for Spartacus
            return """```python
import pytest
from spartacus import is_prime

def test_is_prime_true():
    assert is_prime(7) == True

def test_is_prime_false():
    assert is_prime(4) == False
```"""
        else:
            # Spartacus writes tests for Crixus
            return """```python
import pytest
from crixus import is_prime

def test_prime():
    assert is_prime(11)
    assert not is_prime(10)
```"""

    # Mock for implementation
    if "crixus" in system_prompt.lower():
        return """```python
def is_prime(n):
    \"\"\"Methodical prime checker.\"\"\"
    if n <= 1:
        return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            return False
    return True
```"""
    else:
        return """```python
def is_prime(n):
    # Aggressive prime checker
    if n <= 1: return False
    if n <= 3: return True
    if n % 2 == 0 or n % 3 == 0: return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True
```"""
