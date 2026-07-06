import os
import sys
import subprocess
import json
import urllib.request
import urllib.error
import re

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434/api/generate")
MODEL = os.environ.get("OLLAMA_MODEL", "qwen2.5:0.5b")

def query_ollama(prompt, format_json=False):
    data = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False
    }
    if format_json:
        data["format"] = "json"

    req = urllib.request.Request(OLLAMA_URL, data=json.dumps(data).encode('utf-8'), headers={'Content-Type': 'application/json'})

    try:
        response = urllib.request.urlopen(req)
        result = json.loads(response.read().decode('utf-8'))
        return result.get("response", "")
    except Exception as e:
        print(f"Error querying Ollama: {e}")
        return None

def run_and_fix(filepath, max_iterations=5):
    for iteration in range(1, max_iterations + 1):
        print(f"\n[Iteration {iteration}] Running {filepath}...")

        result = subprocess.run([sys.executable, filepath], capture_output=True, text=True)

        if result.returncode == 0:
            print("Success! Output:")
            print(result.stdout)
            return True

        print("Execution failed. Error:")
        error_msg = result.stderr or result.stdout
        print(error_msg)

        with open(filepath, 'r', encoding='utf-8') as f:
            code = f.read()

        print("Asking Ollama for a fix...")

        prompt = f"""You are an expert Python debugger. The following code throws an error.
Code:
```python
{code}
```

Error:
{error_msg}

Please fix the code. Return ONLY a JSON object with a single key "fixed_code" containing the full updated code.
Example: {{"fixed_code": "print('hello world')"}}
"""
        response_str = query_ollama(prompt, format_json=True)

        if not response_str:
            print("Failed to get response from Ollama.")
            return False

        try:
            response = json.loads(response_str)
            fixed_code = response.get("fixed_code")
            if not fixed_code:
                print("Ollama did not return 'fixed_code'.")
                continue

            print("Applying fix...")
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(fixed_code)

        except json.JSONDecodeError:
            print("Ollama returned invalid JSON.")
            print("Raw response:", response_str)

    print(f"Failed to fix after {max_iterations} iterations.")
    return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python auto_fixer.py <target_script.py>")
        sys.exit(1)

    run_and_fix(sys.argv[1])
