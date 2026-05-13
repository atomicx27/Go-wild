import os
import time
import shutil
import logging
import requests
import subprocess
import json
import datetime
from pathlib import Path

# Setup simple logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("Necromancer")

# Directories
BASE_DIR = Path(__file__).parent
INBOX_DIR = BASE_DIR / "inbox"
OUTBOX_DIR = BASE_DIR / "outbox"
WORKSPACE_DIR = BASE_DIR / "workspace"

OLLAMA_API_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "qwen2.5-coder:7b" # Or whichever robust coding model is default

def ask_ollama(prompt, system_prompt="You are an expert Python data scientist.", temperature=0.1):
    logger.info("Sending prompt to Ollama...")
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "system": system_prompt,
        "stream": False,
        "temperature": temperature
    }

    try:
        response = requests.post(OLLAMA_API_URL, json=payload, timeout=120)
        response.raise_for_status()
        return response.json().get("response", "")
    except requests.exceptions.RequestException as e:
        logger.error(f"Ollama connection error: {e}")
        return None

def extract_code(text):
    """Extracts python code from a markdown block."""
    if not text:
        return ""
    if "```python" in text:
        return text.split("```python")[1].split("```")[0].strip()
    if "```" in text:
        return text.split("```")[1].split("```")[0].strip()
    return text.strip()

def run_code_with_correction(code, script_name, max_retries=3):
    script_path = WORKSPACE_DIR / script_name

    for attempt in range(max_retries):
        with open(script_path, 'w') as f:
            f.write(code)

        logger.info(f"Executing {script_name} (Attempt {attempt+1}/{max_retries})...")
        process = subprocess.run(
            ["python3", str(script_path)],
            capture_output=True,
            text=True,
            cwd=str(WORKSPACE_DIR)
        )

        if process.returncode == 0:
            logger.info(f"{script_name} executed successfully.")
            return process.stdout

        error_output = process.stderr
        logger.warning(f"Execution failed:\n{error_output}")

        if attempt < max_retries - 1:
            logger.info("Asking Ollama to fix the error...")
            prompt = f"""
The following Python script failed with an error.
Please fix the code and return ONLY the corrected Python code. Do not include any explanations.

Original Code:
```python
{code}
```

Error Message:
```
{error_output}
```
            """
            response = ask_ollama(prompt)
            if not response:
                logger.error("Could not reach Ollama for correction.")
                return None

            code = extract_code(response)

    logger.error(f"Failed to execute {script_name} after {max_retries} attempts.")
    return None

def process_file(filepath):
    logger.info(f"Processing new file: {filepath.name}")
    # Move file to workspace
    workspace_path = WORKSPACE_DIR / filepath.name
    try:
        shutil.move(str(filepath), str(workspace_path))
        logger.info(f"Moved {filepath.name} to workspace.")
    except Exception as e:
        logger.error(f"Failed to move {filepath.name}: {e}")
        return

    # Read sample
    try:
        if workspace_path.suffix == '.csv':
            with open(workspace_path, 'r') as f:
                lines = []
                for i, line in enumerate(f):
                    if i >= 5:
                        break
                    lines.append(line)
                sample_data = "".join(lines)
        else:
            with open(workspace_path, 'r') as f:
                sample_data = f.read(500) + "..."
    except Exception as e:
        logger.error(f"Error reading sample: {e}")
        return

    # Generate analysis script
    prompt = f"""
You are a data scientist. Write a Python script using pandas to analyze the following dataset sample.
The file is located at `{workspace_path.name}` in the current directory.
The script should print out basic statistics, check for missing values, and print any interesting insights.
Output ONLY valid Python code inside a markdown block.

Data Sample:
{sample_data}
    """

    response = ask_ollama(prompt)
    if not response:
        return

    code = extract_code(response)
    analysis_output = run_code_with_correction(code, "analyze.py")

    if not analysis_output:
        logger.error("Analysis failed.")
        return

    # Generate visualization script
    viz_prompt = f"""
You are a data visualization expert. Write a Python script using pandas and matplotlib to create ONE meaningful plot for the following dataset sample.
The file is located at `{workspace_path.name}` in the current directory.
The script MUST save the plot as an image file named `plot.png` in the current directory, instead of showing it interactively. Do not use plt.show().
Output ONLY valid Python code inside a markdown block.

Data Sample:
{sample_data}
    """

    viz_response = ask_ollama(viz_prompt)
    if viz_response:
        viz_code = extract_code(viz_response)
        run_code_with_correction(viz_code, "visualize.py")
    else:
        logger.warning("Skipping visualization due to Ollama error.")

    # Generate Markdown Report
    report_prompt = f"""
You are a data analyst. I ran an analysis script on a dataset and got the following output.
Please write a well-formatted Markdown report summarizing these findings.
Include a title, a brief executive summary, and bullet points for key insights.

Analysis Output:
{analysis_output}
    """
    report_response = ask_ollama(report_prompt)
    report_content = report_response if report_response else f"# Data Report\n\n```text\n{analysis_output}\n```"

    report_path = WORKSPACE_DIR / "report.md"
    with open(report_path, 'w') as f:
        f.write(report_content)

    # Bundle and cleanup
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    bundle_name = f"{workspace_path.stem}_bundle_{timestamp}"
    bundle_dir = OUTBOX_DIR / bundle_name
    bundle_dir.mkdir(parents=True, exist_ok=True)

    # Move files to outbox
    try:
        shutil.move(str(workspace_path), str(bundle_dir / workspace_path.name))
        if report_path.exists():
            shutil.move(str(report_path), str(bundle_dir / "report.md"))
        if (WORKSPACE_DIR / "analyze.py").exists():
            shutil.move(str(WORKSPACE_DIR / "analyze.py"), str(bundle_dir / "analyze.py"))
        if (WORKSPACE_DIR / "visualize.py").exists():
            shutil.move(str(WORKSPACE_DIR / "visualize.py"), str(bundle_dir / "visualize.py"))
        if (WORKSPACE_DIR / "plot.png").exists():
            shutil.move(str(WORKSPACE_DIR / "plot.png"), str(bundle_dir / "plot.png"))
        logger.info(f"Successfully bundled analysis into {bundle_name}")
    except Exception as e:
        logger.error(f"Error while bundling files: {e}")

    # Final cleanup of workspace just in case
    for item in WORKSPACE_DIR.iterdir():
        if item.is_file() and item.name != '.gitkeep':
            item.unlink()

def run_loop():
    logger.info("Necromancer Agent started. Monitoring inbox...")
    try:
        while True:
            for item in INBOX_DIR.iterdir():
                if item.is_file() and item.suffix.lower() in ['.csv', '.json']:
                    process_file(item)
            time.sleep(5)
    except KeyboardInterrupt:
        logger.info("Necromancer Agent shutting down.")

if __name__ == "__main__":
    run_loop()
