import json
import requests
import time
import re
import os
import subprocess
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "qwen2.5:0.5b"
console = Console()

def speak(text):
    """Speaks the text using espeak."""
    try:
        # -v en-us (US English), -s 150 (speed), -p 40 (pitch)
        subprocess.run(['espeak', '-v', 'en-us', '-s', '150', '-p', '40', text], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass

def generate_completion(prompt, system_prompt="You are a brilliant software engineer.", max_retries=3):
    payload = {
        "model": MODEL,
        "prompt": prompt,
        "system": system_prompt,
        "stream": False,
        "options": {"temperature": 0.7}
    }

    for attempt in range(max_retries):
        try:
            response = requests.post(OLLAMA_URL, json=payload, timeout=120)
            response.raise_for_status()
            return response.json().get("response", "")
        except requests.exceptions.RequestException as e:
            console.print(f"[bold red]Ollama API error (attempt {attempt + 1}/{max_retries}): {e}[/bold red]")
            if attempt < max_retries - 1:
                time.sleep(2)
            else:
                return ""

def extract_code_blocks(text):
    """Extracts python and html blocks from text."""
    python_pattern = r'```python(.*?)```'
    html_pattern = r'```html(.*?)```'

    python_blocks = re.findall(python_pattern, text, re.DOTALL)
    html_blocks = re.findall(html_pattern, text, re.DOTALL)

    return {
        "python": "\n".join(b.strip() for b in python_blocks),
        "html": "\n".join(b.strip() for b in html_blocks)
    }

class AgentManager:
    def __init__(self, inbox_dir="inbox", outbox_dir="outbox"):
        self.inbox_dir = inbox_dir
        self.outbox_dir = outbox_dir
        os.makedirs(self.inbox_dir, exist_ok=True)
        os.makedirs(self.outbox_dir, exist_ok=True)

    def process_idea(self, filepath):
        with open(filepath, 'r') as f:
            idea = f.read()

        idea_name = os.path.basename(filepath).split('.')[0]
        console.print(Panel(f"Forging: {idea_name}", style="cyan"))
        speak(f"Beginning forge process for {idea_name}")

        project_dir = os.path.join(self.outbox_dir, idea_name)
        os.makedirs(project_dir, exist_ok=True)

        # 1. Architect: Breakdown
        console.print("[yellow]Phase 1: Architecting[/yellow]")
        speak("Phase 1. Architecting the solution.")
        arch_prompt = f"Break down this idea into a simple single-file Python script or HTML file. Provide the complete code for it. Idea: {idea}"
        system_prompt = "You are a master architect. Only output valid code in markdown blocks."

        spec = generate_completion(arch_prompt, system_prompt=system_prompt)

        blocks = extract_code_blocks(spec)

        # Determine main language
        if blocks['html'] and not blocks['python']:
             code_content = blocks['html']
             ext = "html"
        elif blocks['python'] and not blocks['html']:
             code_content = blocks['python']
             ext = "py"
        else:
            # Default to py if both or neither (fallback to raw if neither)
             code_content = blocks['python'] or spec
             ext = "py"

        if not code_content.strip():
            code_content = "# AI failed to generate code\n" + spec

        main_file = os.path.join(project_dir, f"app.{ext}")
        with open(main_file, "w") as f:
            f.write(code_content)

        console.print(f"[green]Saved to {main_file}[/green]")
        speak(f"Code saved to {ext} file.")

        # 2. QA: Test (if Python)
        if ext == "py":
            console.print("[yellow]Phase 2: QA Testing (Self-Healing Loop)[/yellow]")
            speak("Phase 2. Initiating Quality Assurance testing.")
            for _ in range(3): # max 3 fixes
                # Use a timeout and pipe yes to handle input() calls
                try:
                    result = subprocess.run(["python3", main_file], capture_output=True, text=True, input="Test\n", timeout=15)
                    if result.returncode == 0:
                        console.print("[green]Execution successful![/green]")
                        speak("Execution successful. No errors detected.")
                        break
                    else:
                        console.print(f"[red]Error detected:[/red]\n{result.stderr}")
                        speak("Error detected. Engaging self-healing sequence.")
                        fix_prompt = f"The following code failed:\n```python\n{code_content}\n```\nError:\n{result.stderr}\nFix the code and output only the complete corrected code in a ```python``` block."
                        fixed_code_raw = generate_completion(fix_prompt)
                        fixed_blocks = extract_code_blocks(fixed_code_raw)
                        if fixed_blocks['python']:
                            code_content = fixed_blocks['python']
                            with open(main_file, "w") as f:
                                f.write(code_content)
                            console.print("[cyan]Applied fix, retrying...[/cyan]")
                            speak("Fix applied. Retrying execution.")
                        else:
                            console.print("[red]AI failed to provide a fix block.[/red]")
                            speak("Critical failure. AI unable to provide a fix.")
                            break
                except subprocess.TimeoutExpired:
                    console.print("[red]Execution timed out (likely an infinite loop).[/red]")
                    speak("Execution timed out. Engaging self-healing sequence.")
                    fix_prompt = f"The following code timed out during execution:\n```python\n{code_content}\n```\nEnsure there are no infinite loops or hanging input calls. Provide the complete corrected code in a ```python``` block."
                    fixed_code_raw = generate_completion(fix_prompt)
                    fixed_blocks = extract_code_blocks(fixed_code_raw)
                    if fixed_blocks['python']:
                        code_content = fixed_blocks['python']
                        with open(main_file, "w") as f:
                            f.write(code_content)
                        console.print("[cyan]Applied fix, retrying...[/cyan]")
                        speak("Fix applied. Retrying execution.")
                    else:
                        console.print("[red]AI failed to provide a fix block.[/red]")
                        speak("Critical failure. AI unable to provide a fix.")
                        break


        os.remove(filepath)
        console.print(f"[bold magenta]Project '{idea_name}' forged successfully![/bold magenta]")
        speak(f"Project {idea_name} forged successfully. Awaiting next command.")


if __name__ == "__main__":
    manager = AgentManager()
    console.print("[bold green]Soul Forge initialized and watching inbox...[/bold green]")
    speak("Soul Forge initialized and watching inbox.")
    while True:
        try:
            for filename in os.listdir(manager.inbox_dir):
                if filename.endswith(".txt"):
                    filepath = os.path.join(manager.inbox_dir, filename)
                    manager.process_idea(filepath)
            time.sleep(2)
        except KeyboardInterrupt:
            speak("Shutting down Soul Forge.")
            break
