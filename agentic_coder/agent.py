import sys
import json
import requests
import subprocess
import time
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt

console = Console()

def generate_code(prompt_text, error_msg=None, previous_code=None):
    url = "http://localhost:11434/api/generate"

    sys_prompt = (
        "You are an expert Python developer. Write the complete, runnable Python code "
        "to accomplish the user's task. Output ONLY the raw Python code, without any Markdown "
        "formatting like ```python or explanations. Your entire response must be valid Python code."
    )

    if error_msg and previous_code:
        prompt_text = (
            f"The previous code you generated failed with the following error:\n"
            f"```\n{error_msg}\n```\n"
            f"Here is the code that failed:\n"
            f"```python\n{previous_code}\n```\n"
            f"Please fix the code to accomplish the original task: {prompt_text}"
        )
    else:
        prompt_text = f"Task: {prompt_text}"

    data = {
        "model": "qwen2.5:0.5b",
        "prompt": f"{sys_prompt}\n\n{prompt_text}",
        "stream": False
    }

    try:
        response = requests.post(url, json=data, timeout=60)
        response.raise_for_status()
        code = response.json()['response'].strip()

        # Strip markdown if the model still outputs it despite instructions
        if code.startswith("```python"):
            code = code[9:]
        elif code.startswith("```"):
            code = code[3:]
        if code.endswith("```"):
            code = code[:-3]

        return code.strip()
    except Exception as e:
        console.print(f"[bold red]Error communicating with Ollama: {e}[/bold red]")
        return None

def execute_code(code, filename="generated_script.py"):
    with open(filename, "w") as f:
        f.write(code)

    try:
        result = subprocess.run(
            ["python3", filename],
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Execution timed out."
    except Exception as e:
        return False, "", str(e)

def main():
    if len(sys.argv) < 2:
        console.print("[bold red]Usage: python3 agent.py \"your task description\"[/bold red]")
        sys.exit(1)

    task = " ".join(sys.argv[1:])
    console.print(Panel(f"[bold cyan]Task:[/bold cyan] {task}", title="🤖 Agentic Coder Starting"))

    # Warmup request
    try:
        requests.post("http://localhost:11434/api/generate", json={"model": "qwen2.5:0.5b", "prompt": "hi", "stream": False}, timeout=10)
    except:
        pass

    max_retries = 3
    current_retry = 0
    error_msg = None
    previous_code = None

    while current_retry <= max_retries:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        ) as progress:
            status = "Generating code..." if current_retry == 0 else f"Fixing code (Attempt {current_retry}/{max_retries})..."
            progress.add_task(description=status, total=None)

            code = generate_code(task, error_msg, previous_code)

        if not code:
            console.print("[bold red]Failed to generate code.[/bold red]")
            break

        console.print(f"\n[bold green]Generated Code (Attempt {current_retry}):[/bold green]")
        syntax = Syntax(code, "python", theme="monokai", line_numbers=True)
        console.print(Panel(syntax))

        choice = Prompt.ask("⚠️ Execute this AI-generated code on your system?", choices=["y", "n"], default="n")
        if choice != "y":
            console.print("[yellow]Execution cancelled by user.[/yellow]")
            break

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        ) as progress:
            progress.add_task(description="Executing code...", total=None)
            success, stdout, stderr = execute_code(code)

        if success:
            console.print("[bold green]✅ Execution Successful![/bold green]")
            if stdout:
                console.print(Panel(stdout, title="Output", border_style="green"))
            break
        else:
            console.print("[bold red]❌ Execution Failed![/bold red]")
            console.print(Panel(stderr, title="Error Log", border_style="red"))

            error_msg = stderr
            previous_code = code
            current_retry += 1

            if current_retry <= max_retries:
                console.print("[bold yellow]Retrying to fix the error...[/bold yellow]\n")
                time.sleep(2) # brief pause before retry
            else:
                console.print("[bold red]Max retries reached. Task failed.[/bold red]")

if __name__ == "__main__":
    main()
