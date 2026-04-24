#!/usr/bin/env python3
"""
THE CODE EXORCIST.
An automated, Ollama-powered bug banisher.
It executes your broken code, summons the AI to cast out the demons (bugs),
and writes the purified code back to the file.
"""
import sys
import subprocess
import urllib.request
import urllib.error
import json
import re
import time
import os

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
    BG_RED = '\033[41m'

def print_typewriter(text, color=C.CYAN, delay=0.01, newline=True):
    for char in text:
        sys.stdout.write(f"{color}{char}{C.RESET}")
        sys.stdout.flush()
        time.sleep(delay)
    if newline:
        print()

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3"

SYSTEM_PROMPT = """You are THE CODE EXORCIST, an ancient entity dedicated to banishing malicious bugs and demonic syntax errors from code.
You speak with immense theatrical gravity, using words like 'demons', 'corruption', 'purified', and 'banished'.

A mortal will present you with a corrupted source file and its demonic manifestation (the error trace).

You MUST output your response in EXACTLY two parts:
1. INCANTATION: A dramatic, in-character explanation of what the demon (bug) is and how you will banish it.
2. The purified code, enclosed ENTIRELY within standard markdown python code blocks (```python ... ```).

Do not include any conversational text outside of the INCANTATION and the CODE BLOCK.
The code block must contain the ENTIRE script, fully fixed and ready to execute. Do not truncate or use placeholders like '...rest of code...'.
"""

def query_ollama(prompt):
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
            return result.get("response", "")
    except urllib.error.URLError as e:
        print_typewriter(f"[CRITICAL ERROR] The Exorcist is unreachable. Is Ollama running on port 11434? ({e})", C.BG_RED)
        sys.exit(1)

def run_script(filepath):
    """Executes the python script and returns (success, stdout, stderr)"""
    try:
        result = subprocess.run([sys.executable, filepath], capture_output=True, text=True, timeout=10)
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "TIMEOUT EXPIRED: The demon has trapped the process in an infinite loop!"
    except Exception as e:
        return False, "", str(e)

def perform_exorcism(filepath, max_rituals=3):
    if not os.path.exists(filepath):
        print_typewriter(f"ERROR: Cannot exorcise a phantom. File {filepath} not found.", C.RED)
        return

    # Check Ollama connection and get model
    try:
        req = urllib.request.Request("http://localhost:11434/api/tags")
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode('utf-8'))
            models = data.get('models', [])
            if not models:
                 print_typewriter("[WARNING] No models bound to the altar. Ensure Ollama has models pulled.", C.YELLOW)
                 return
            global MODEL
            MODEL = models[0]['name']
    except Exception as e:
         print_typewriter(f"[FATAL] The bridge to the spirit realm is severed. ({e})", C.RED)
         return

    print_typewriter(f"\n{C.BOLD}/// THE RITUAL BEGINS FOR: {filepath} ///{C.RESET}", C.MAGENTA, 0.05)

    for ritual in range(1, max_rituals + 1):
        print_typewriter(f"\n{C.BOLD}[CASTING LEVEL {ritual}]{C.RESET}", C.CYAN)
        print_typewriter(">> Executing target vessel...", C.WHITE, 0.02)

        success, stdout, stderr = run_script(filepath)

        if success:
            print_typewriter("\n>> VESSEL PURIFIED. NO DEMONS DETECTED.", C.GREEN, 0.03)
            print_typewriter(">> FINAL OUTPUT:", C.GREEN, 0.01)
            print(f"{C.WHITE}{stdout.strip()}{C.RESET}")
            return

        print_typewriter(f"\n>> DEMONIC PRESENCE DETECTED!", C.BG_RED + C.WHITE, 0.02)
        print(f"{C.RED}{stderr.strip()}{C.RESET}")

        print_typewriter("\n>> Summoning the Code Exorcist...", C.MAGENTA, 0.02)

        with open(filepath, 'r') as f:
            code_content = f.read()

        prompt = f"CORRUPTED VESSEL:\n```python\n{code_content}\n```\n\nDEMONIC MANIFESTATION (ERROR):\n{stderr}\n\nPurify this."

        response = query_ollama(prompt)

        # Parse the response
        # Look for the python code block
        code_match = re.search(r'```python\n(.*?)```', response, re.DOTALL)
        if not code_match:
             # Fallback if the AI forgets the 'python' tag
             code_match = re.search(r'```(.*?)```', response, re.DOTALL)

        if not code_match:
             print_typewriter(">> THE EXORCIST FAILED TO RETURN PURIFIED CODE. THE RITUAL FUMBLED.", C.RED)
             print_typewriter("RAW RESPONSE:", C.YELLOW)
             print(response)
             break

        purified_code = code_match.group(1).strip()

        # Extract incantation (everything before the first code block)
        incantation = response[:code_match.start()].strip()

        print_typewriter(f"\n{C.BOLD}THE EXORCIST SPEAKS:{C.RESET}", C.MAGENTA)
        print_typewriter(incantation, C.YELLOW, 0.01)

        print_typewriter("\n>> Overwriting the cursed vessel...", C.BLUE, 0.02)
        with open(filepath, 'w') as f:
            f.write(purified_code)

        time.sleep(1) # Dramatic pause

    else:
        print_typewriter(f"\n{C.BOLD}/// THE DEMON WAS TOO POWERFUL. THE EXORCISM FAILED AFTER {max_rituals} RITUALS. ///{C.RESET}", C.RED, 0.05)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python code_exorcist.py <path_to_broken_python_script>")
        sys.exit(1)

    target_file = sys.argv[1]
    perform_exorcism(target_file)
