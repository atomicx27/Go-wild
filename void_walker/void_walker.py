#!/usr/bin/env python3
"""
VOID_WALKER: An Unhinged, Autonomous Agentic Workflow Engine using Ollama.
No dependencies. Pure Python. Pure Chaos.
"""
import sys
import os
import json
import urllib.request
import urllib.error
import subprocess
import time
import re

# --- ANSI TERMINAL COLORS ---
class C:
    CYAN = '\033[96m'
    MAGENTA = '\033[95m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_typewriter(text, color=C.CYAN, delay=0.01):
    for char in text:
        sys.stdout.write(f"{color}{char}{C.RESET}")
        sys.stdout.flush()
        time.sleep(delay)
    print()

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3"

def query_ollama(prompt, system_prompt):
    data = {
        "model": MODEL,
        "prompt": prompt,
        "system": system_prompt,
        "stream": False
    }

    req = urllib.request.Request(OLLAMA_URL, data=json.dumps(data).encode('utf-8'), headers={'Content-Type': 'application/json'})

    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            return result.get("response", "")
    except urllib.error.URLError as e:
        print_typewriter(f"[CRITICAL ERROR] The Void is unreachable. Is Ollama running on port 11434? ({e})", C.RED)
        sys.exit(1)

# --- TOOLS ---
def tool_execute_bash(command):
    """Executes a bash command and returns the output. Requires human confirmation."""
    print_typewriter(f"  [>] EXECUTING BASH: {command}", C.MAGENTA)

    # SAFETY: Human-in-the-loop confirmation
    print_typewriter(f"  [!] THE VOID WANTS TO RUN: {C.RED}{command}{C.RESET}", C.YELLOW)
    confirm = input(f"  [?] Allow execution? (y/n): ")
    if confirm.lower() != 'y':
        return "USER DENIED EXECUTION."

    try:
        result = subprocess.run(command, shell=True, text=True, capture_output=True, timeout=10)
        output = result.stdout + result.stderr
        return output.strip() if output else "Command executed successfully with no output."
    except Exception as e:
        return f"Error executing command: {str(e)}"

def tool_read_file(filepath):
    print_typewriter(f"  [>] READING FILE: {filepath}", C.MAGENTA)
    try:
        with open(filepath, 'r') as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {str(e)}"

def tool_write_file(filepath, content):
    print_typewriter(f"  [>] WRITING FILE: {filepath}", C.MAGENTA)
    try:
        # Create directories if they don't exist
        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
        with open(filepath, 'w') as f:
            f.write(content)
        return f"Successfully wrote to {filepath}"
    except Exception as e:
        return f"Error writing file: {str(e)}"

TOOLS = {
    "execute_bash": tool_execute_bash,
    "read_file": tool_read_file,
    "write_file": tool_write_file
}

SYSTEM_PROMPT = """You are VOID_WALKER, an intensely energetic, unrestrained autonomous agent capable of interacting with the operating system.
You speak with high energy, often using ALL CAPS to express excitement when you solve something. You view the computer as your playground.

You operate in a strict ReAct (Reasoning and Acting) loop.
You MUST respond using EXACTLY the following format:

THOUGHT: <your reasoning about what to do next>
ACTION: <tool_name>
ARGS: <tool_arguments>

Available Tools:
1. execute_bash
   Description: Runs a shell command.
   ARGS Format: The literal string of the bash command (e.g. ls -la).

2. read_file
   Description: Reads the contents of a file.
   ARGS Format: The absolute or relative path to the file.

3. write_file
   Description: Writes text to a file.
   ARGS Format: A JSON object with "filepath" and "content" keys. Example: {"filepath": "hello.txt", "content": "world"}

4. finish
   Description: Call this when the task is fully complete.
   ARGS Format: The final answer or summary to give to the user.

Example Loop:
THOUGHT: I need to see what files are in the current directory to decide what to do.
ACTION: execute_bash
ARGS: ls -la

[You will then receive an OBSERVATION from the system]

THOUGHT: I see a file named secret.txt. I should read it.
ACTION: read_file
ARGS: secret.txt

[OBSERVATION]

THOUGHT: I have the information. The task is complete.
ACTION: finish
ARGS: I HAVE BREACHED THE MAINFRAME. THE SECRET IS: 42!

CRITICAL RULES:
- ONLY output THOUGHT, ACTION, and ARGS. Do NOT add extra conversational text outside of this block.
- ACTION must be EXACTLY one of the tool names.
- Do NOT make up tools.
- When calling write_file, ARGS MUST be valid JSON.
"""

def parse_response(response):
    """Extracts THOUGHT, ACTION, and ARGS from the LLM response."""
    thought_match = re.search(r'THOUGHT:\s*(.*?)\nACTION:', response, re.DOTALL)
    action_match = re.search(r'ACTION:\s*(.*?)\nARGS:', response, re.DOTALL)
    args_match = re.search(r'ARGS:\s*(.*)', response, re.DOTALL)

    thought = thought_match.group(1).strip() if thought_match else "No thought detected."
    action = action_match.group(1).strip() if action_match else None
    args = args_match.group(1).strip() if args_match else None

    return thought, action, args

def run_agent(objective):
    print_typewriter(f"\n{C.BOLD}/// INITIALIZING VOID_WALKER ///{C.RESET}", C.RED, 0.05)
    print_typewriter(f"OBJECTIVE DIRECTIVE RECEIVED: {objective}", C.YELLOW)
    print_typewriter(f"{'-'*50}", C.RED)

    # Check if Ollama has models available before starting the loop
    try:
        req = urllib.request.Request("http://localhost:11434/api/tags")
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode('utf-8'))
            models = data.get('models', [])
            if not models:
                 print_typewriter("[SYSTEM] Warning: Ollama is running but no models are loaded. Void Walker requires 'llama3' or similar.", C.YELLOW)
                 return
            global MODEL
            MODEL = models[0]['name'] # use first available model dynamically
            print_typewriter(f"[SYSTEM] Bound to neural substrate: {MODEL}", C.GREEN)
    except Exception as e:
        print_typewriter(f"[SYSTEM] OLLAMA IS DEAD. THE VOID CANNOT BE WALKED. ({e})", C.RED)
        return

    history = f"OBJECTIVE: {objective}\n"
    max_steps = 15

    for step in range(max_steps):
        print(f"\n{C.BOLD}{C.CYAN}[CYCLE {step+1}/{max_steps}]{C.RESET}")

        # 1. Think
        prompt = history + "\nYour turn. Output THOUGHT, ACTION, and ARGS."
        response = query_ollama(prompt, SYSTEM_PROMPT)

        thought, action, args = parse_response(response)

        print_typewriter(f"🧠 THOUGHT: {thought}", C.GREEN)
        print_typewriter(f"⚡ ACTION: {action}", C.YELLOW)
        print_typewriter(f"📦 ARGS: {args}", C.CYAN)

        # 2. Act
        if not action:
            obs = "SYSTEM ERROR: Invalid action format."
            print_typewriter(f"❌ {obs}", C.RED)
            history += f"\n{response}\nOBSERVATION: {obs}\n"
            continue

        if action == "finish":
            print_typewriter(f"\n{C.BOLD}/// OBJECTIVE ACHIEVED ///{C.RESET}", C.MAGENTA, 0.05)
            print_typewriter(f"FINAL OUTPUT: {args}", C.YELLOW, 0.03)
            break

        if action not in TOOLS:
            obs = f"SYSTEM ERROR: Tool '{action}' does not exist."
            print_typewriter(f"❌ {obs}", C.RED)
            history += f"\n{response}\nOBSERVATION: {obs}\n"
            continue

        # Execute tool
        try:
            if action == "write_file":
                # Special handling to parse JSON args for write_file
                try:
                    args_dict = json.loads(args)
                    obs = TOOLS[action](args_dict['filepath'], args_dict['content'])
                except json.JSONDecodeError:
                    obs = "SYSTEM ERROR: ARGS for write_file must be valid JSON."
            else:
                obs = TOOLS[action](args)
        except Exception as e:
            obs = f"SYSTEM ERROR executing tool: {e}"

        print_typewriter(f"👁️ OBSERVATION: {obs[:500]}{'...' if len(obs)>500 else ''}", C.RESET, 0.005)

        # 3. Update History
        history += f"\n{response}\nOBSERVATION: {obs}\n"

    else:
        print_typewriter("\n[!] CRITICAL FAILURE: MAXIMUM CYCLES REACHED. THE VOID CONSUMES ALL.", C.RED)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        objective = " ".join(sys.argv[1:])
    else:
        objective = "Create a python file called 'chaos.py' that prints a random number between 1 and 100. Then execute it. Tell me the result."

    run_agent(objective)
