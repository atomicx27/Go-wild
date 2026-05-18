import os
import time
import json
import urllib.request
import urllib.error
import glob
import shutil
import argparse

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434/api/generate")
MODEL = os.environ.get("OLLAMA_MODEL", "llama3.1")

INBOX_DIR = "app_smith/inbox"
OUTBOX_DIR = "app_smith/outbox"
PROCESSED_DIR = "app_smith/processed"

def query_ollama(prompt, format_json=False):
    """Queries the Ollama API."""
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

def process_idea(file_path):
    """Processes a single idea file."""
    print(f"\n[App Smith] Processing idea from {file_path}...")

    with open(file_path, 'r') as f:
        idea = f.read().strip()

    if not idea:
        print(f"[App Smith] Empty idea in {file_path}. Skipping.")
        return False

    app_name = os.path.basename(file_path).replace('.txt', '')
    app_outbox = os.path.join(OUTBOX_DIR, app_name)
    os.makedirs(app_outbox, exist_ok=True)

    # 1. Ask for architecture
    print(f"[App Smith] Designing architecture for '{app_name}'...")
    arch_prompt = f"""
    You are an expert software architect.
    The user wants to build this application: "{idea}"

    Design the file structure for this application.
    Return ONLY a JSON object representing the files to be created.
    The keys should be the file paths relative to the project root, and the values should be a short description of what the file should contain.

    Example:
    {{
        "index.html": "The main HTML file",
        "style.css": "The main stylesheet",
        "app.js": "The main logic"
    }}
    """

    arch_json_str = query_ollama(arch_prompt, format_json=True)
    if not arch_json_str:
        print("[App Smith] Failed to get architecture from Ollama.")
        return False

    try:
        architecture = json.loads(arch_json_str)
    except json.JSONDecodeError:
        print("[App Smith] Ollama returned invalid JSON for architecture.")
        print("Raw response:", arch_json_str)
        return False

    print(f"[App Smith] Planned {len(architecture)} files.")

    # 2. Generate code for each file
    for rel_path, description in architecture.items():
        print(f"  [App Smith] Generating code for {rel_path}...")

        # Ensure subdirectories exist
        full_path = os.path.join(app_outbox, rel_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)

        code_prompt = f"""
        You are an expert software developer.
        The user wants to build this application: "{idea}"

        You are writing the file `{rel_path}`.
        Its purpose is: {description}

        Here is the planned architecture for context:
        {json.dumps(architecture, indent=2)}

        Write the complete, functional code for `{rel_path}`.
        Do not include any markdown formatting like ```html or ```python around the code.
        Just return the raw code that can be written directly to the file.
        """

        code = query_ollama(code_prompt)
        if code is None:
            print(f"  [App Smith] Failed to generate code for {rel_path}.")
            continue

        # Clean up possible markdown fences if the model ignored instructions
        if code.startswith("```"):
            code = code.split("\n", 1)[1]
        if code.endswith("```"):
            code = code.rsplit("\n", 1)[0]

        with open(full_path, 'w') as f:
            f.write(code.strip())

    print(f"[App Smith] Successfully forged '{app_name}' in {app_outbox}!")
    return True

def main():
    parser = argparse.ArgumentParser(description="App Smith - Autonomous App Builder")
    parser.add_argument("--run-once", action="store_true", help="Run once and exit instead of polling")
    args = parser.parse_args()

    # Ensure all root directories exist
    os.makedirs(INBOX_DIR, exist_ok=True)
    os.makedirs(OUTBOX_DIR, exist_ok=True)
    os.makedirs(PROCESSED_DIR, exist_ok=True)

    print("[App Smith] The Forge Master is awake and watching the inbox...")

    while True:
        idea_files = glob.glob(os.path.join(INBOX_DIR, "*.txt"))

        for file_path in idea_files:
            success = process_idea(file_path)

            if success:
                # Move to processed
                shutil.move(file_path, os.path.join(PROCESSED_DIR, os.path.basename(file_path)))
            else:
                # rename to indicate failure so we don't keep trying
                os.rename(file_path, file_path + ".failed")

        if args.run_once:
            break

        time.sleep(5)

if __name__ == "__main__":
    main()
