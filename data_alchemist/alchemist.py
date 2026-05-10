import os
import time
import shutil
import urllib.request
import json
import subprocess
import re
from pathlib import Path

# Directories
BASE_DIR = Path(__file__).resolve().parent
INBOX_DIR = BASE_DIR / "inbox"
OUTBOX_DIR = BASE_DIR / "outbox"
WORKSPACE_DIR = BASE_DIR / "workspace"
ARCHIVE_DIR = BASE_DIR / "archive"

# Ensure directories exist
for d in [INBOX_DIR, OUTBOX_DIR, WORKSPACE_DIR, ARCHIVE_DIR]:
    d.mkdir(parents=True, exist_ok=True)

OLLAMA_URL = "http://localhost:11434/api/chat"
OLLAMA_MODEL = "llama3"

def call_ollama(prompt: str) -> str:
    print("Calling Ollama...")
    data = json.dumps({
        "model": OLLAMA_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "stream": False
    }).encode('utf-8')

    req = urllib.request.Request(OLLAMA_URL, data=data, headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            result = json.loads(response.read().decode('utf-8'))
            return result['message']['content']
    except Exception as e:
        print(f"Ollama API error ({e}). Using mock fallback.")
        return get_mock_response(prompt)

def get_mock_response(prompt: str) -> str:
    # A mock response that generates a simple python script
    return '''Here is a script to process the data:
```python
import sys

input_file = sys.argv[1]
output_file = sys.argv[2]

print(f"Mock processing {input_file} -> {output_file}")
with open(input_file, 'r') as f_in, open(output_file, 'w') as f_out:
    data = f_in.read()
    f_out.write("Processed by Data Alchemist Mock Agent:")
    f_out.write(data.upper())
```
'''

def extract_code(text: str) -> str:
    # Look for python code block
    match = re.search(r"```python\s+(.*?)\s+```", text, re.DOTALL)
    if match:
        return match.group(1)

    # Fallback to any code block
    match = re.search(r"```.*?\s+(.*?)\s+```", text, re.DOTALL)
    if match:
        return match.group(1)

    return text.strip()

def process_file(filepath: Path):
    print(f"\nProcessing new file: {filepath.name}")

    # Read sample data
    try:
        with open(filepath, 'r') as f:
            data_sample = f.read(1024) # read up to 1KB
    except Exception as e:
        print(f"Error reading file {filepath.name}: {e}")
        return

    base_prompt = f"""You are the Data Alchemist.
I have a file named '{filepath.name}'.
Here is a sample of its contents:
---
{data_sample}
---
Write a Python script that takes two command line arguments:
1. input_filepath
2. output_filepath

The script should read the input file, perform some interesting transformation or analysis, and write the results to the output file.
Return ONLY the python code inside ```python ``` blocks. Do not explain anything else."""

    MAX_RETRIES = 3

    output_filename = f"out_{filepath.stem}.txt"
    output_path = OUTBOX_DIR / output_filename

    # Script file path
    script_path = WORKSPACE_DIR / f"script_{filepath.stem}.py"

    current_prompt = base_prompt

    for attempt in range(MAX_RETRIES):
        print(f"Attempt {attempt + 1} of {MAX_RETRIES} to generate script...")
        response = call_ollama(current_prompt)

        script_code = extract_code(response)

        with open(script_path, 'w') as f:
            f.write(script_code)

        print(f"Generated script saved to {script_path.name}. Executing...")

        try:
            # Execute the script
            result = subprocess.run(
                ["python3", str(script_path), str(filepath), str(output_path)],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                print(f"Execution successful! Artifact created at {output_path.name}")
                break
            else:
                print(f"Execution failed with code {result.returncode}.")
                error_msg = result.stderr.strip() or result.stdout.strip()
                print(f"Error:\n{error_msg}\n")

                # Agentic self-healing
                current_prompt = f"""The previous python script you provided failed to execute.
Here was the error output:
---
{error_msg}
---
Please rewrite the script to fix this error.
Remember, the script must take `input_filepath` and `output_filepath` as sys.argv[1] and sys.argv[2].
Return ONLY the fixed python code inside ```python ``` blocks."""

        except subprocess.TimeoutExpired:
            print("Execution timed out. Retrying...")
            current_prompt = f"The previous script timed out. Please write a simpler script that finishes faster."
        except Exception as e:
            print(f"Unexpected error during execution: {e}")
            break

    else:
        print("Max retries reached. Could not process file successfully.")

    # Move to archive
    print(f"Finished processing {filepath.name}. Moving to archive...")
    archive_path = ARCHIVE_DIR / filepath.name
    # Handle duplicates in archive by appending a timestamp if needed
    if archive_path.exists():
        archive_path = ARCHIVE_DIR / f"{filepath.stem}_{int(time.time())}{filepath.suffix}"

    shutil.move(str(filepath), str(archive_path))
    print(f"Archived to {archive_path}")

def poll_inbox(interval_seconds=5):
    print(f"Started polling {INBOX_DIR} every {interval_seconds} seconds...")
    try:
        while True:
            for filepath in INBOX_DIR.iterdir():
                if filepath.is_file() and not filepath.name.startswith('.'):
                    process_file(filepath)
            time.sleep(interval_seconds)
    except KeyboardInterrupt:
        print("\nStopping polling loop.")

if __name__ == "__main__":
    poll_inbox()
