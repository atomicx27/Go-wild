import os
import re
import sys
import subprocess
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

from llm import generate_code

console = Console()

def extract_python_code(text: str) -> str:
    """Extracts python code from a markdown-formatted string."""
    match = re.search(r"```python(.*?)```", text, re.DOTALL)
    if match:
        return match.group(1).strip()

    # fallback if no markdown block
    return text.strip()

def run_code(code: str) -> str:
    """Saves the code to a temporary file, runs it, and returns the output."""
    temp_file = "temp_generated.py"
    try:
        with open(temp_file, "w") as f:
            f.write(code)

        result = subprocess.run(["python3", temp_file], capture_output=True, text=True, timeout=10)

        output = f"Stdout:\n{result.stdout}\n"
        if result.stderr:
             output += f"Stderr:\n{result.stderr}\n"
        return output
    except subprocess.TimeoutExpired:
        return "Execution timed out after 10 seconds."
    except Exception as e:
        return f"Error executing code: {e}"
    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)

def main():
    console.print(Panel.fit("[bold green]Welcome to Agentic Coder![/bold green]", border_style="green"))
    console.print("Type your task below, and I will generate and run the Python code for you.")
    console.print("Type 'exit' or 'quit' to exit.")

    while True:
        try:
            task = console.input("\n[bold cyan]Task:[/bold cyan] ")
            if task.lower() in ['exit', 'quit']:
                console.print("Exiting...")
                break

            if not task.strip():
                continue

            # Step 1: Prompt generation
            prompt = (
                f"You are an expert Python developer. Please write a Python script to accomplish the following task: {task}\n"
                "Please output ONLY the raw Python code within a ```python ``` block. "
                "Do not explain the code or add extra text."
            )

            console.print("[yellow]Generating code...[/yellow]")
            response = generate_code(prompt)

            # Step 2: Code extraction
            code = extract_python_code(response)

            if not code or code.startswith("Error"):
                console.print(f"[bold red]Failed to generate code:[/bold red] {response}")
                continue

            console.print("\n[bold green]Generated Code:[/bold green]")
            console.print(Markdown(f"```python\n{code}\n```"))

            # Step 3: Confirmation and Execution
            confirm = console.input("\n[bold yellow]Do you want to run this code? (y/n): [/bold yellow]").strip().lower()
            if confirm in ['y', 'yes']:
                console.print("\n[yellow]Executing code...[/yellow]")
                output = run_code(code)

                console.print("\n[bold blue]Execution Output:[/bold blue]")
                console.print(output)
            else:
                console.print("\n[blue]Code execution skipped.[/blue]")

        except EOFError:
            break
        except KeyboardInterrupt:
            console.print("\nExiting...")
            break

if __name__ == "__main__":
    main()
