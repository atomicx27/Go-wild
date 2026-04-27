import sys
import subprocess
import os
import json
import urllib.request
import urllib.error
import re
import time

def run_script(script_path):
    print(f"Running {script_path}...")
    result = subprocess.run([sys.executable, script_path], capture_output=True, text=True)
    return result

def query_ollama(prompt, model="llama3"):
    ollama_url = os.environ.get("OLLAMA_URL", "http://localhost:11434")
    url = f"{ollama_url}/api/generate"
    data = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }
    req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers={'Content-Type': 'application/json'})

    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            return result.get("response", "")
    except urllib.error.URLError as e:
        print(f"Error connecting to Ollama: {e}")
        return ""

def extract_code(text):
    # Try to extract code blocks using regex
    code_blocks = re.findall(r'```python\n(.*?)\n```', text, re.DOTALL)
    if not code_blocks:
        code_blocks = re.findall(r'```\n(.*?)\n```', text, re.DOTALL)

    if code_blocks:
        # Return the longest code block found (assuming it's the full script)
        return max(code_blocks, key=len)

    # If no code blocks found, return the original text if it looks like python,
    # otherwise we might just return empty and fail
    if "def " in text or "import " in text or "print" in text:
         return text.strip()

    return ""

def heal_script(script_path, max_retries=3):
    for attempt in range(max_retries):
        result = run_script(script_path)

        if result.returncode == 0:
            print("Script ran successfully!")
            if result.stdout:
                print("Output:")
                print(result.stdout)
            return True

        print(f"Attempt {attempt + 1} failed.")
        print(f"Error Output:\n{result.stderr}")

        if attempt == max_retries - 1:
            print("Max retries reached. Could not heal the script.")
            return False

        print("Consulting Ollama for a fix...")

        with open(script_path, 'r') as f:
            source_code = f.read()

        prompt = f"""
I have a Python script that is throwing an error. Please fix the code.
Return ONLY the complete, fixed Python code inside a ```python ``` codeblock. Do not include any explanation.

Source Code:
```python
{source_code}
```

Error Traceback:
{result.stderr}
"""

        response = query_ollama(prompt)

        if not response:
            print("Failed to get a response from Ollama. Aborting.")
            return False

        fixed_code = extract_code(response)

        if not fixed_code:
            print("Could not extract fixed code from Ollama's response. Aborting.")
            print(f"Raw response: {response}")
            return False

        print("Applying fix and retrying...")
        with open(script_path, 'w') as f:
            f.write(fixed_code)

        time.sleep(1) # Give it a brief pause before retrying

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python phoenix.py <path_to_script>")
        sys.exit(1)

    script_to_run = sys.argv[1]

    if not os.path.exists(script_to_run):
        print(f"Error: Script '{script_to_run}' not found.")
        sys.exit(1)

    heal_script(script_to_run)
