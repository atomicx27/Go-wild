import time
import os
import sys
import threading
import json
import pandas as pd
import requests
import subprocess
import tempfile
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

INPUT_DIR = "input"
OUTPUT_DIR = "output"
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "qwen2.5-coder:7b"

class DataFileHandler(FileSystemEventHandler):
    def __init__(self, alchemist):
        self.alchemist = alchemist

    def on_created(self, event):
        if event.is_directory:
            return

        filepath = event.src_path
        if filepath.endswith('.csv') or filepath.endswith('.json'):
            print(f"[+] New data file detected: {filepath}")
            self.alchemist.process_file(filepath)

class DataAlchemist:
    def __init__(self, input_dir=INPUT_DIR, output_dir=OUTPUT_DIR):
        self.input_dir = os.path.abspath(input_dir)
        self.output_dir = os.path.abspath(output_dir)

        os.makedirs(self.input_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)

        self.observer = Observer()

    def query_ollama(self, prompt, context=""):
        full_prompt = f"{context}\n\n{prompt}" if context else prompt
        payload = {
            "model": MODEL_NAME,
            "prompt": full_prompt,
            "stream": False
        }

        try:
            print(f"[*] Asking Ollama for insights...")
            response = requests.post(OLLAMA_URL, json=payload)
            response.raise_for_status()
            result = response.json()
            return result.get('response', '')
        except requests.exceptions.RequestException as e:
            print(f"[-] Failed to communicate with Ollama: {e}")
            return None

    def extract_code(self, response):
        """Extracts python code from markdown block if present."""
        if "```python" in response:
            parts = response.split("```python")
            if len(parts) > 1:
                code_part = parts[1].split("```")[0]
                return code_part.strip()
        elif "```" in response:
            parts = response.split("```")
            if len(parts) > 1:
                code_part = parts[1].split("```")[0]
                return code_part.strip()
        return response.strip()

    def generate_eda_code(self, filepath, data_sample, columns):
        prompt = f"""
You are an expert Data Scientist. I have a dataset located at: `{filepath}`.
The dataset has the following columns: {columns}.
Here is a sample of the first 5 rows:
{data_sample}

Write a comprehensive Python script using pandas and matplotlib/seaborn to perform Exploratory Data Analysis (EDA) on this dataset.
The script should:
1. Load the dataset from the absolute path provided: `{filepath}`.
2. Clean the data if necessary (handle missing values, correct types).
3. Generate at least 3 insightful visualizations.
4. Save all visualizations as PNG files in the absolute directory: `{self.output_dir}`.
5. Print out a summary of the findings to stdout.
6. The script MUST run independently. Do NOT ask for input. Do NOT show GUI windows (`plt.show()`), only save to files (`plt.savefig()`).

Output ONLY the Python code inside a ```python ``` markdown block. Do not provide explanations.
"""
        return self.query_ollama(prompt)

    def execute_and_heal(self, code, max_retries=3):
        for attempt in range(1, max_retries + 1):
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(code)
                script_path = f.name

            print(f"[*] Attempt {attempt}: Executing generated EDA script...")

            try:
                result = subprocess.run([sys.executable, script_path], capture_output=True, text=True, check=True)
                print("[+] Script executed successfully!")
                print("--- Script Output ---")
                print(result.stdout)
                print("---------------------")
                os.remove(script_path)
                return True
            except subprocess.CalledProcessError as e:
                print(f"[-] Script execution failed. Error trace:")
                print(e.stderr)

                if attempt == max_retries:
                    print("[-] Max retries reached. Could not fix the code.")
                    os.remove(script_path)
                    return False

                print("[*] Asking Ollama to fix the code...")
                prompt = f"""
The following Python script failed to execute.
Here is the script:
```python
{code}
```

Here is the error traceback:
```
{e.stderr}
```

Please fix the script based on the error.
The script MUST run independently, load data from the specified path, perform EDA, and save plots to the `{self.output_dir}` directory.

Output ONLY the corrected Python code inside a ```python ``` markdown block. Do not provide explanations.
"""
                raw_response = self.query_ollama(prompt)
                if not raw_response:
                    print("[-] Ollama failed to respond during healing phase.")
                    os.remove(script_path)
                    return False
                code = self.extract_code(raw_response)
                os.remove(script_path)

    def process_file(self, filepath):
        print(f"\n[*] Processing file: {filepath}")
        try:
            if filepath.endswith('.csv'):
                df = pd.read_csv(filepath)
            elif filepath.endswith('.json'):
                df = pd.read_json(filepath)
            else:
                return

            columns = list(df.columns)
            data_sample = df.head().to_string()

            print(f"[*] Dataset loaded. {len(df)} rows, {len(columns)} columns.")

            raw_response = self.generate_eda_code(filepath, data_sample, columns)
            if not raw_response:
                return

            code = self.extract_code(raw_response)

            print("[+] Ollama generated the EDA code.")

            self.execute_and_heal(code)

        except Exception as e:
            print(f"[-] Error reading data file: {e}")

    def start_monitoring(self):
        event_handler = DataFileHandler(self)
        self.observer.schedule(event_handler, self.input_dir, recursive=False)
        self.observer.start()
        print(f"[*] Data Alchemist started. Monitoring '{self.input_dir}' for .csv and .json files...")

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.observer.stop()
            print("\n[-] Data Alchemist stopped.")

        self.observer.join()

if __name__ == "__main__":
    alchemist = DataAlchemist()
    alchemist.start_monitoring()
