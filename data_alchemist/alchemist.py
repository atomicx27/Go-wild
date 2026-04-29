import os
import time
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
