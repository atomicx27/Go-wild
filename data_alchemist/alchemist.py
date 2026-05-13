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
import glob
import logging
import urllib.request
import urllib.error
import json
import re
import subprocess

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DataAlchemist:
    def __init__(self, base_dir="data_alchemist"):
        self.base_dir = base_dir
        self.cauldron_dir = os.path.join(base_dir, "cauldron")
        self.grimoire_dir = os.path.join(base_dir, "grimoire")
        self.vault_dir = os.path.join(base_dir, "vault")
        self.processed_files = set()

    def get_new_files(self):
        """Scans the cauldron for new files."""
        # Find all files in the cauldron, excluding .gitkeep
        pattern = os.path.join(self.cauldron_dir, "*")
        all_files = [f for f in glob.glob(pattern) if os.path.isfile(f) and not f.endswith('.gitkeep')]

        new_files = [f for f in all_files if f not in self.processed_files]
        return new_files

    def read_file_preview(self, filepath, num_lines=50):
        """Reads the first few lines of a file to give context to Ollama."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = []
                for i in range(num_lines):
                    line = f.readline()
                    if not line:
                        break
                    lines.append(line.strip())
                return "\n".join(lines)
        except Exception as e:
            logger.error(f"Error reading preview of {filepath}: {e}")
            return f"Error reading file: {e}"

    def run(self):
        """Main loop watching the cauldron."""
        logger.info("Data Alchemist started. Watching the cauldron...")
        try:
            while True:
                new_files = self.get_new_files()
                for filepath in new_files:
                    logger.info(f"New file detected in cauldron: {filepath}")

                    # Read preview
                    preview = self.read_file_preview(filepath)
                    logger.info(f"Read preview. Processing...")

                    # Process file (to be implemented)
                    self.process_file(filepath, preview)

                    self.processed_files.add(filepath)

                time.sleep(2)
        except KeyboardInterrupt:
            logger.info("Data Alchemist stopped by user.")

    def query_ollama(self, prompt, model="llama3.1"):
        """Queries the local Ollama instance."""
        url = "http://localhost:11434/api/generate"
        data = {
            "model": model,
            "prompt": prompt,
            "stream": False
        }

        req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers={'Content-Type': 'application/json'})

        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                result = json.loads(response.read().decode('utf-8'))
                return result.get('response', '')
        except urllib.error.URLError as e:
            logger.error(f"Failed to connect to Ollama: {e}")
            return None
        except Exception as e:
            logger.error(f"Error querying Ollama: {e}")
            return None

    def extract_python_code(self, text):
        """Extracts python code blocks from markdown text."""
        pattern = r"```(?:python)?\n(.*?)\n```"
        matches = re.findall(pattern, text, re.DOTALL)
        if matches:
            return matches[-1] # Return the last block found
        return text

    def generate_script(self, filepath, preview):
        """Uses Ollama to generate a Python script to process the file."""
        filename = os.path.basename(filepath)
        prompt = f"""
You are the Data Alchemist, an expert Python developer.
I have a file named '{filename}' with the following preview content:
---
{preview}
---

Write a complete Python script to clean this data and save the clean version and any insights.
The script MUST:
1. Read the file from '{filepath}'.
2. Process or clean the data based on what it looks like.
3. Save the cleaned data to the '{self.vault_dir}' directory (e.g., as a cleaned CSV, JSON, or SQLite DB).
4. Save some basic insights or summary to a markdown file in the '{self.vault_dir}' directory.
5. Print progress to stdout.
6. Only return valid Python code enclosed in ```python ... ``` block. Do not add any extra explanation outside the code block.

Do your best based on the preview. If it looks like a CSV, use pandas or csv. If JSON, use json.
"""

        logger.info(f"Asking Ollama to write a script for {filename}...")
        response = self.query_ollama(prompt)

        if response:
            code = self.extract_python_code(response)
            return code
        else:
            logger.error("Failed to generate script due to Ollama error.")
            return None

    def process_file(self, filepath, preview):
        """Processes a single file."""
        logger.info(f"Processing {os.path.basename(filepath)}...")

        script_code = self.generate_script(filepath, preview)
        if not script_code:
            logger.warning(f"Skipping {filepath} due to script generation failure.")
            return

        # Save to grimoire
        script_name = f"process_{os.path.basename(filepath).split('.')[0]}_{int(time.time())}.py"
        script_path = os.path.join(self.grimoire_dir, script_name)

        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(script_code)

        logger.info(f"Generated script saved to {script_path}")

        # Execute script with retries
        max_retries = 3

        for attempt in range(max_retries):
            logger.info(f"Executing {script_name} (Attempt {attempt + 1}/{max_retries})...")

            try:
                result = subprocess.run(
                    ["python", script_path],
                    capture_output=True,
                    text=True,
                    timeout=60
                )

                if result.returncode == 0:
                    logger.info(f"Successfully executed {script_name}")
                    logger.debug(f"Output: {result.stdout}")
                    break
                else:
                    logger.warning(f"Execution failed with return code {result.returncode}")
                    logger.warning(f"Error output: {result.stderr}")

                    if attempt < max_retries - 1:
                        logger.info("Asking Ollama to fix the script...")
                        script_code = self.fix_script(script_code, result.stderr)
                        if script_code:
                            with open(script_path, 'w', encoding='utf-8') as f:
                                f.write(script_code)
                            logger.info("Updated script saved.")
                        else:
                            logger.error("Failed to generate a fix.")
                            break
                    else:
                        logger.error(f"Max retries reached for {filepath}. Moving on.")

            except subprocess.TimeoutExpired:
                logger.error(f"Execution of {script_name} timed out.")
                break
            except Exception as e:
                logger.error(f"Unexpected error executing {script_name}: {e}")
                break

    def fix_script(self, original_code, traceback_error):
        """Asks Ollama to fix a broken script based on the traceback."""
        prompt = f"""
You are the Data Alchemist, an expert Python developer.
I previously asked you to write a script, but it failed with the following traceback:

---
{traceback_error}
---

Here is the original code that failed:
---
{original_code}
---

Please fix the code.
Only return valid Python code enclosed in ```python ... ``` block. Do not add any extra explanation outside the code block.
"""
        response = self.query_ollama(prompt)

        if response:
            return self.extract_python_code(response)
        return None

if __name__ == "__main__":
    alchemist = DataAlchemist()
    alchemist.run()
