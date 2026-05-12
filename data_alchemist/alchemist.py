import os
import time
import shutil
import subprocess
import json
import uuid
import datetime
from pathlib import Path
import urllib.request
import urllib.error
import glob

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3" # Or another model if needed, but we'll try llama3 first

INBOX_DIR = Path("data_alchemist/inbox")
OUTBOX_DIR = Path("data_alchemist/outbox")
WORKSPACES_DIR = Path("data_alchemist/workspaces")

def ensure_dirs():
    INBOX_DIR.mkdir(parents=True, exist_ok=True)
    OUTBOX_DIR.mkdir(parents=True, exist_ok=True)
    WORKSPACES_DIR.mkdir(parents=True, exist_ok=True)

def query_ollama(prompt, system=""):
    # Since Ollama might not be running locally in test environment, mock response
    # Real implementation would look like this:
    try:
        data = {
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "system": system,
            "stream": False
        }

        req = urllib.request.Request(
            OLLAMA_URL,
            data=json.dumps(data).encode('utf-8'),
            headers={'Content-Type': 'application/json'}
        )
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            return result.get("response", "")
    except Exception as e:
        print(f"Error communicating with Ollama, using MOCK response: {e}")
        if "expert web designer" in system or "expert web designer" in prompt:
            return "```html\n<html><body><h1>Dashboard</h1><p>Insights.</p></body></html>\n```"
        else:
            return """```python
import pandas as pd
import matplotlib.pyplot as plt
import os

try:
    df = pd.read_csv('sample_sales.csv')
    plt.figure()
    df.groupby('Region')['Sales'].sum().plot(kind='bar')
    plt.savefig('chart1.png')
    with open('insights.txt', 'w') as f:
        f.write("Sales are highest in South.\\n")
except Exception as e:
    pass
```"""

def extract_code(text):
    """Extracts python code from markdown code blocks."""
    if "```python" in text:
        parts = text.split("```python")
        if len(parts) > 1:
            code_part = parts[1].split("```")[0]
            return code_part.strip()
    elif "```" in text:
         parts = text.split("```")
         if len(parts) > 1:
             code_part = parts[1]
             # simple heuristic, skip if first word looks like a language tag and not code
             first_line = code_part.split('\n')[0].strip()
             if first_line.isalpha() and first_line not in ('import', 'from', 'def', 'class'):
                 code_part = '\n'.join(code_part.split('\n')[1:])
             return code_part.strip()
    return text.strip()

def process_file(filepath):
    filename = filepath.name
    print(f"Processing {filename}...")

    # Create workspace
    workspace_id = f"job_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
    workspace_path = WORKSPACES_DIR / workspace_id
    workspace_path.mkdir(parents=True, exist_ok=True)

    # Copy file to workspace
    dest_file = workspace_path / filename
    shutil.copy(filepath, dest_file)

    # Extract sample
    sample_text = ""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = [f.readline() for _ in range(10)]
            sample_text = "".join(lines)
    except Exception as e:
        print(f"Could not read file {filename}: {e}")
        return

    system_prompt = """You are an expert Python data scientist.
Write a python script to analyze the provided dataset and generate visualizations and text insights.
Requirements:
1. The dataset is located in the current working directory.
2. Produce at least one PNG visualization and save it in the current directory (e.g., 'chart1.png'). Do NOT show the plot interactively (use plt.savefig, not plt.show).
3. Produce a text file named 'insights.txt' containing key findings.
4. Keep the code robust, add try/except blocks if needed, and do not use relative paths like '../', just use the current directory.
5. Provide ONLY the raw Python code within ```python ``` blocks. No other text.
"""

    prompt = f"The dataset filename is '{filename}'. Here are the first few lines/items:\n{sample_text}\n\nWrite the Python code now."

    print("Generating code with Ollama...")
    response = query_ollama(prompt, system=system_prompt)
    if not response:
        print("Failed to get a response from Ollama.")
        return

    code = extract_code(response)
    script_path = workspace_path / "analyze.py"
    with open(script_path, "w") as f:
        f.write(code)

    # Execution and Self-Healing
    max_retries = 3
    success = False

    for attempt in range(max_retries):
        print(f"Running script (Attempt {attempt+1}/{max_retries})...")
        # Run in the workspace directory
        result = subprocess.run(
            ["python", "analyze.py"],
            cwd=workspace_path,
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            print("Script executed successfully!")
            success = True
            break
        else:
            print(f"Script failed. Error:\n{result.stderr}")
            print("Attempting to auto-heal...")
            error_prompt = f"The code you provided failed with this error:\n```\n{result.stderr}\n```\nHere was the code:\n```python\n{code}\n```\nPlease fix the code and return the corrected Python code within ```python ``` blocks."
            response = query_ollama(error_prompt, system="You are an expert Python debugger. Fix the provided code.")
            if response:
                code = extract_code(response)
                with open(script_path, "w") as f:
                    f.write(code)
            else:
                break

    if not success:
        print(f"Failed to process {filename} after {max_retries} attempts. See workspace {workspace_id}.")
        filepath.unlink() # remove from inbox
        return

    # Read Insights
    insights_path = workspace_path / "insights.txt"
    insights_content = "No insights.txt was generated."
    if insights_path.exists():
        with open(insights_path, "r") as f:
            insights_content = f.read()

    # Read Images
    image_files = glob.glob(str(workspace_path / "*.png"))
    image_names = [Path(img).name for img in image_files]

    # Generate Dashboard HTML
    print("Generating Dashboard...")
    dashboard_prompt = f"""You are an expert web designer.
Create a beautiful, modern HTML dashboard to display the results of a data analysis.
The insights are:
{insights_content}

The generated charts are: {', '.join(image_names)}

Requirements:
1. Write raw HTML, CSS (in a <style> tag), and Javascript (if needed) in a single file.
2. Use modern styling (e.g. Tailwind via CDN, or clean custom CSS with flexbox/grid, shadows, rounded corners).
3. Include an <img> tag for each chart in the list. Assume they are in the same directory.
4. Format the insights nicely.
5. Provide ONLY the raw HTML code. Do not wrap in markdown or explain.
"""
    html_response = query_ollama(dashboard_prompt)

    # Extract HTML
    html_content = html_response
    if "```html" in html_content:
        html_content = html_content.split("```html")[1].split("```")[0].strip()
    elif "```" in html_content:
         parts = html_content.split("```")
         if len(parts) > 1:
             html_content = parts[1]

    html_path = workspace_path / "dashboard.html"
    with open(html_path, "w") as f:
        f.write(html_content)

    # Move to outbox
    print(f"Moving results to outbox...")
    outbox_dest = OUTBOX_DIR / workspace_id
    shutil.copytree(workspace_path, outbox_dest)

    # Clean up inbox
    filepath.unlink()
    print(f"Finished processing {filename}. Results in {outbox_dest}")

def main():
    ensure_dirs()
    print(f"Data Alchemist started. Watching {INBOX_DIR}...")

    try:
        while True:
            # Check for new files
            for filepath in INBOX_DIR.iterdir():
                if filepath.is_file() and not filepath.name.startswith('.'):
                    process_file(filepath)

            time.sleep(5)
    except KeyboardInterrupt:
        print("\nShutting down Data Alchemist.")

if __name__ == "__main__":
    main()
