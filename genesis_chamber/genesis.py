import urllib.request
import urllib.error
import json
import os
import sys
import re
import time
import datetime
from pathlib import Path

OLLAMA_API_URL = os.environ.get("OLLAMA_API_URL", "http://localhost:11434")

def get_available_model():
    """Probes Ollama for available models and returns the first one, or 'mock' if unreachable."""
    try:
        req = urllib.request.Request(f"{OLLAMA_API_URL}/api/tags")
        with urllib.request.urlopen(req, timeout=2) as response:
            data = json.loads(response.read().decode())
            if data and "models" in data and len(data["models"]) > 0:
                model_names = [m["name"] for m in data["models"]]
                for pref in ["llama3", "mistral", "phi3"]:
                    for m in model_names:
                        if pref in m:
                            return m
                return data["models"][0]["name"]
    except Exception:
        pass
    return "mock"

def generate_text(prompt, model="mock", system=""):
    """Communicates with Ollama or returns a mock response if model is 'mock'."""
    if model == "mock":
        return f"[MOCK FILE BLOCK]\n===FILE: src/main.py===\nprint('Hello from mock for: {prompt[:30]}...')\n===ENDFILE==="

    try:
        payload = {
            "model": model,
            "prompt": prompt,
            "system": system,
            "stream": False,
            "options": {
                "temperature": 0.7
            }
        }
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(f"{OLLAMA_API_URL}/api/generate", data=data, headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(req, timeout=120) as response:
            result = json.loads(response.read().decode())
            return result.get("response", "")
    except Exception as e:
        print(f"\n[Error generating text: {e}]")
        return f"[FALLBACK RESPONSE due to error: {e}]\n===FILE: fallback.txt===\nError: {e}\n===ENDFILE==="

def print_colored(text, color_code):
    print(f"\033[{color_code}m{text}\033[0m")

def run_pipeline(idea, model):
    """Runs the 4-stage multi-agent pipeline."""

    print_colored(f"\n--- 1. The Visionary (Expanding Idea) ---", "36")
    sys_visionary = "You are a visionary product manager. Expand the following raw idea into a comprehensive, ambitious product vision."
    vision = generate_text(f"Idea: {idea}", model=model, system=sys_visionary)
    print(vision[:500] + "...\n(Truncated for display)")

    print_colored(f"\n--- 2. The Critic (Scoping to MVP) ---", "31")
    sys_critic = "You are a ruthless technical critic. Take the provided product vision and strip it down to a bare-bones, achievable Minimum Viable Product (MVP). Focus on core mechanics only."
    mvp = generate_text(f"Vision:\n{vision}", model=model, system=sys_critic)
    print(mvp[:500] + "...\n(Truncated for display)")

    print_colored(f"\n--- 3. The Architect (System Design) ---", "33")
    sys_architect = "You are a software architect. Take the MVP description and output a clear file structure and technology stack. Be concise."
    architecture = generate_text(f"MVP:\n{mvp}", model=model, system=sys_architect)
    print(architecture[:500] + "...\n(Truncated for display)")

    print_colored(f"\n--- 4. The Coder (Implementation) ---", "32")
    sys_coder = """You are a master programmer. Implement the provided architecture.
You MUST output code files using the following exact format for EVERY file:

===FILE: relative/path/to/file.ext===
<file contents here>
===ENDFILE===

Do not include any explanations outside these blocks, or if you do, keep them brief. Output ALL necessary files to make the MVP run."""
    code_output = generate_text(f"Architecture:\n{architecture}", model=model, system=sys_coder)
    print(code_output[:500] + "...\n(Truncated for display)")

    return code_output

def parse_and_write_files(code_output, project_name):
    """Parses the Coder's output and writes the files to a new directory in outbox."""
    outbox_dir = Path(__file__).parent / "outbox" / project_name
    outbox_dir.mkdir(parents=True, exist_ok=True)

    pattern = re.compile(r"===FILE:\s*(.+?)===\n(.*?)(?:\n===ENDFILE===)", re.DOTALL)
    matches = pattern.findall(code_output)

    if not matches:
        print_colored(f"No files parsed from output. Saving raw output to raw_output.txt", "31")
        with open(outbox_dir / "raw_output.txt", "w", encoding="utf-8") as f:
            f.write(code_output)
        return

    for filepath, content in matches:
        filepath = filepath.strip()
        if ".." in filepath or filepath.startswith("/"):
            print_colored(f"Skipping dangerous filepath: {filepath}", "31")
            continue

        full_path = outbox_dir / filepath
        full_path.parent.mkdir(parents=True, exist_ok=True)

        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)
        print_colored(f"Created file: {full_path}", "32")

def process_idea(idea_text, idea_name):
    model = get_available_model()
    print_colored(f"Starting Genesis Chamber for: {idea_name} (Using model: {model})", "35")

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    project_name = f"{idea_name}_{timestamp}"

    code_output = run_pipeline(idea_text, model)
    parse_and_write_files(code_output, project_name)
    print_colored(f"Finished processing {idea_name}. Output saved to outbox/{project_name}", "35")

def watch_inbox():
    """Watches the inbox directory for new .txt files and processes them."""
    inbox_dir = Path(__file__).parent / "inbox"
    inbox_dir.mkdir(parents=True, exist_ok=True)
    print_colored(f"Watching inbox directory: {inbox_dir}...", "34")

    processed_files = set()

    try:
        while True:
            for file_path in inbox_dir.glob("*.txt"):
                if file_path.name not in processed_files:
                    print_colored(f"New idea found: {file_path.name}", "34")
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            idea_text = f.read().strip()

                        if idea_text:
                            idea_name = file_path.stem.replace(" ", "_")
                            process_idea(idea_text, idea_name)

                        # Move processed file to prevent reprocessing or delete it
                        processed_file_path = file_path.with_suffix(".txt.processed")
                        file_path.rename(processed_file_path)
                        print_colored(f"Marked {file_path.name} as processed.", "34")
                        processed_files.add(processed_file_path.name)

                    except Exception as e:
                        print_colored(f"Error processing {file_path.name}: {e}", "31")
            time.sleep(2)
    except KeyboardInterrupt:
        print_colored("Stopping inbox watcher.", "34")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "--watch":
            watch_inbox()
        else:
            idea = sys.argv[1]
            process_idea(idea, "cli_idea")
    else:
        print("Usage: python genesis.py 'Your idea here' OR python genesis.py --watch")
