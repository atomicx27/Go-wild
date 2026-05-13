import argparse
import urllib.request
import json
import sys
import subprocess
import os
import re
import hashlib
import time
from rich.console import Console
from rich.syntax import Syntax
from rich.panel import Panel

console = Console()

OLLAMA_URL = "http://localhost:11434/api/generate"

def query_ollama(prompt, model="llama3.2"):
    data = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }

    req = urllib.request.Request(
        OLLAMA_URL,
        data=json.dumps(data).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )

    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode("utf-8"))
            return result.get("response", "")
    except Exception as e:
        print(f"Error communicating with Ollama: {e}", file=sys.stderr)
        return None

def extract_python_code(text):
    """Extracts Python code from a markdown block."""
    match = re.search(r"```python\s*(.*?)\s*```", text, re.DOTALL)
    if match:
        return match.group(1)
    # If no markdown block, return the whole text, maybe it's just code
    return text

def execute_script(script_path):
    """Executes the script and returns (success_bool, stdout, stderr)."""
    try:
        result = subprocess.run(["python", script_path], capture_output=True, text=True, timeout=60)
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Execution timed out after 60 seconds."
    except Exception as e:
        return False, "", str(e)

def main():
    parser = argparse.ArgumentParser(description="Archmage: An agentic AI CLI tool.")
    parser.add_argument("spell", help="The natural language command to execute.")
    parser.add_argument("--model", default="llama3.2", help="The Ollama model to use (default: llama3.2).")
    parser.add_argument("--retries", type=int, default=3, help="Number of times to retry fixing the script.")

    args = parser.parse_args()

    console.print(Panel(f"[bold magenta]Casting spell:[/bold magenta] '{args.spell}'\n[dim]Model: {args.model}[/dim]", border_style="magenta"))

    # Setup grimoire directory
    grimoire_dir = os.path.join(os.path.dirname(__file__), "grimoire")
    os.makedirs(grimoire_dir, exist_ok=True)

    spell_hash = hashlib.md5(args.spell.encode()).hexdigest()[:8]
    script_path = os.path.join(grimoire_dir, f"spell_{spell_hash}.py")

    prompt = f"""
You are a master wizard programmer.
Write a python script to accomplish the following spell (task): {args.spell}

Return ONLY the python code inside a ```python ``` block. Do not add any extra explanations.
If it requires pip packages, write them as comments at the top like # REQUIRES: package1 package2
"""

    with console.status("[bold cyan]Consulting the arcane texts (Ollama)...", spinner="star"):
        response = query_ollama(prompt, args.model)

    if not response:
        console.print("[bold red]Failed to contact the arcane forces (Ollama).[/bold red]")
        sys.exit(1)

    code = extract_python_code(response)

    with open(script_path, "w") as f:
        f.write(code)

    console.print(f"[green]Spell transcribed to {script_path}.[/green]")
    console.print(Panel(Syntax(code, "python", theme="monokai", line_numbers=True), title="Incantation", border_style="cyan"))

    success = False
    for attempt in range(args.retries + 1):
        with console.status(f"[bold yellow]Executing spell (Attempt {attempt+1})...", spinner="moon"):
            success, stdout, stderr = execute_script(script_path)

        if success:
            console.print("[bold green]✨ Spell executed successfully! ✨[/bold green]")
            if stdout:
                console.print(Panel(stdout, title="Output", border_style="green"))
            break
        else:
            if attempt < args.retries:
                console.print(f"[bold red]Spell failed![/bold red] (Attempt {attempt+1}/{args.retries}). Modifying incantation...")
                console.print(Panel(stderr, title="Error Output", border_style="red"))

                fix_prompt = f"""
The following python code failed to execute.
Code:
```python
{code}
```

Error:
{stderr}

Please fix the code. Return ONLY the fixed python code inside a ```python ``` block.
"""
                with console.status("[bold magenta]Weaving fixes into the spell...", spinner="aesthetic"):
                    response = query_ollama(fix_prompt, args.model)

                if not response:
                    console.print("[bold red]Failed to contact Ollama for fixes.[/bold red]")
                    break

                code = extract_python_code(response)
                with open(script_path, "w") as f:
                    f.write(code)

                console.print("[cyan]Updated Incantation:[/cyan]")
                console.print(Panel(Syntax(code, "python", theme="monokai", line_numbers=True), title="Incantation v2", border_style="cyan"))
            else:
                console.print("[bold red]The spell is too broken. The magic fizzles out.[/bold red]")
                console.print(Panel(stderr, title="Final Error Output", border_style="red"))

if __name__ == "__main__":
    main()
