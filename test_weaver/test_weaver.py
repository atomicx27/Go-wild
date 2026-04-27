import argparse
import sys
import os
import requests
import json
import re
import subprocess
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()

def parse_arguments():
    parser = argparse.ArgumentParser(description="Test Weaver: AI-Agentic Pytest Generator")
    parser.add_argument("target_file", help="The Python file to generate tests for.")
    parser.add_argument("--model", default="llama3", help="The Ollama model to use (default: llama3)")
    parser.add_argument("--url", default="http://localhost:11434/api/generate", help="Ollama API URL")
    parser.add_argument("--retries", type=int, default=3, help="Max self-correction retries (default: 3)")
    return parser.parse_args()

def extract_python_code(text):
    match = re.search(r'```python\n(.*?)\n```', text, re.DOTALL)
    if match:
        return match.group(1).strip()
    # Fallback to returning everything if no code blocks are found
    return text.strip()

def call_ollama(prompt, model, url):
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }
    try:
        response = requests.post(url, json=payload, timeout=60)
        response.raise_for_status()
        return response.json().get("response", "")
    except Exception as e:
        console.print(f"[bold red]Error communicating with Ollama:[/] {e}")
        return None

def run_tests(test_file):
    try:
        result = subprocess.run(
            ["pytest", test_file, "-v"],
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.returncode == 0, result.stdout + result.stderr
    except Exception as e:
        return False, str(e)

def main():
    args = parse_arguments()

    if not os.path.exists(args.target_file):
        console.print(f"[bold red]Error:[/] File '{args.target_file}' does not exist.")
        sys.exit(1)

    console.print(Panel(f"Test Weaver started for: [bold cyan]{args.target_file}[/]", title="Init", border_style="cyan"))

    with open(args.target_file, "r") as f:
        source_code = f.read()

    test_file_name = f"test_{os.path.basename(args.target_file)}"
    test_file_path = os.path.join(os.path.dirname(args.target_file), test_file_name)

    base_prompt = f"""
You are an expert Python test engineer. Write a complete, runnable `pytest` suite for the following code.
Only return the Python code inside a ```python ``` block. Include all necessary imports.

Source code ({args.target_file}):
```python
{source_code}
```
"""
    current_prompt = base_prompt
    success = False

    for attempt in range(1, args.retries + 1):
        console.print(f"\n[bold yellow]Attempt {attempt}/{args.retries}[/]")

        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
            task = progress.add_task(f"Generating tests via Ollama ({args.model})...", total=None)
            response_text = call_ollama(current_prompt, args.model, args.url)
            progress.update(task, completed=True)

        if not response_text:
            break

        test_code = extract_python_code(response_text)

        with open(test_file_path, "w") as f:
            f.write(test_code)

        console.print(f"[green]Tests written to {test_file_path}[/]")

        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
            task = progress.add_task("Running pytest...", total=None)
            passed, output = run_tests(test_file_path)
            progress.update(task, completed=True)

        if passed:
            console.print(Panel("[bold green]All tests passed successfully![/]", title="Success", border_style="green"))
            success = True
            break
        else:
            console.print(Panel(f"[bold red]Tests Failed.[/]\n\n{output[-1000:]}", title="Test Failure", border_style="red"))

            current_prompt = f"""
The tests you generated previously failed. Please fix the tests.
Only return the corrected Python code inside a ```python ``` block.

Original source code:
```python
{source_code}
```

Failing test output:
```text
{output}
```
"""

    if not success:
        console.print("[bold red]Agent failed to generate passing tests after maximum retries.[/]")

if __name__ == "__main__":
    main()
