#!/usr/bin/env python3
"""
THE DOCU-DEMON.
An aggressive, Ollama-powered auto-documenter.
It tears through your codebase, analyzing undocumented chaos,
and violently injects comprehensive, PEP-compliant docstrings and comments.
No external dependencies.
"""
import sys
import os
import urllib.request
import urllib.error
import json
import re
import time

# --- ANSI TERMINAL COLORS ---
class C:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_typewriter(text, color=C.CYAN, delay=0.005, newline=True):
    for char in text:
        sys.stdout.write(f"{color}{char}{C.RESET}")
        sys.stdout.flush()
        time.sleep(delay)
    if newline:
        print()

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3"

SYSTEM_PROMPT = """You are THE DOCU-DEMON. Your sole purpose is to consume raw, undocumented Python code and violently inject perfectly formatted, PEP 257 compliant docstrings and insightful inline comments.
You MUST follow these rules absolutely:
1. You MUST return the ENTIRE python script. Do not truncate, summarize, or use placeholders like '# ... rest of code ...'.
2. Do NOT change any of the underlying logic, variable names, or behavior of the code. Only add comments and docstrings.
3. Every class and function MUST have a comprehensive docstring detailing its purpose, Args, and Returns.
4. Add inline comments explaining complex or non-obvious logic.
5. Your output MUST consist ONLY of the documented code, wrapped exactly in a single ```python code block. No conversational text. No explanations.
"""

ASCII_ART = fr"""{C.RED}{C.BOLD}
   ,   ,
  /(   )\\
  \ \_/ /   THE DOCU-DEMON AWAKENS
   |- -|    AUTO-DOCUMENTATION PROTOCOL ENGAGED
  /  _  \\
 / /   \ \\
 \ \   / /
  \_>-<_/
{C.RESET}"""

def get_model():
    try:
        req = urllib.request.Request("http://localhost:11434/api/tags")
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode('utf-8'))
            models = data.get('models', [])
            if not models:
                 print_typewriter("[WARNING] No models found in Ollama. Ensure you have pulled a model.", C.YELLOW)
                 return None
            return models[0]['name']
    except Exception as e:
         print_typewriter(f"[FATAL] Cannot connect to Ollama on port 11434. The Demon sleeps. ({e})", C.RED)
         return None

def document_code(code_content):
    prompt = f"DOCUMENT THIS CHAOS:\n```python\n{code_content}\n```"
    data = {
        "model": MODEL,
        "prompt": prompt,
        "system": SYSTEM_PROMPT,
        "stream": False
    }

    req = urllib.request.Request(OLLAMA_URL, data=json.dumps(data).encode('utf-8'), headers={'Content-Type': 'application/json'})

    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            res_text = result.get("response", "")

            # Parse markdown python block
            code_match = re.search(r'```python\n(.*?)```', res_text, re.DOTALL)
            if not code_match:
                 code_match = re.search(r'```(.*?)```', res_text, re.DOTALL)

            if code_match:
                return code_match.group(1).strip()
            else:
                return res_text.strip() # Fallback, assume they just output the code

    except Exception as e:
        print_typewriter(f"  [!] Failed to invoke the oracle: {e}", C.RED)
        return None

def process_directory(target_dir):
    print(ASCII_ART)
    print_typewriter(f">> ASSESSING DOMAIN: {os.path.abspath(target_dir)}", C.CYAN)

    target_files = []
    for root, _, files in os.walk(target_dir):
        for file in files:
            if file.endswith('.py') and file != os.path.basename(__file__):
                target_files.append(os.path.join(root, file))

    if not target_files:
        print_typewriter(">> NO SACRIFICES (PYTHON FILES) FOUND.", C.YELLOW)
        return

    print_typewriter(f">> LOCATED {len(target_files)} UNDOCUMENTED VESSELS.", C.MAGENTA)
    print_typewriter("-" * 50, C.RED)

    for filepath in target_files:
        print_typewriter(f"[*] RIPPING INTO: {filepath}", C.YELLOW, 0.01)

        with open(filepath, 'r') as f:
            original_code = f.read()

        print_typewriter(f"    - Consuming {len(original_code)} bytes...", C.CYAN)

        documented_code = document_code(original_code)

        if documented_code:
            # Basic sanity check to avoid overwriting with garbage if the model hallucinates
            if len(documented_code) < len(original_code) * 0.5:
                 print_typewriter(f"    - [!] REJECTED. The Demon returned an empty husk (output too short).", C.RED)
                 continue

            with open(filepath, 'w') as f:
                f.write(documented_code)
            print_typewriter(f"    - [✓] KNOWLEDGE INJECTED. FILE OVERWRITTEN.", C.GREEN)
        else:
            print_typewriter(f"    - [X] EXORCISM FAILED FOR THIS FILE.", C.RED)

    print_typewriter("-" * 50, C.RED)
    print_typewriter(f"\n{C.BOLD}/// DOCU-DEMON HAS FINISHED ITS RAMPAGE ///{C.RESET}", C.MAGENTA)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python docu_demon.py <path_to_directory>")
        sys.exit(1)


    MODEL = get_model()
    if not MODEL:
        sys.exit(1)

    target_dir = sys.argv[1]
    process_directory(target_dir)
