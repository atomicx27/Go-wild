import sys
import json
import subprocess
import requests
import re
from rich.console import Console
from rich.markdown import Markdown

console = Console()

OLLAMA_API = "http://localhost:11434/api/generate"
MODEL = "qwen2.5-coder:1.5b"
MAX_RETRIES = 3

def generate_code(prompt: str, context: list) -> str:
    """Queries Ollama to generate Python code based on prompt and history."""

    system_prompt = "You are an expert Python coder. Write standard Python 3 code to satisfy the user's prompt. ONLY return valid Python code enclosed in ```python ... ``` blocks. Do not add explanations outside the block."

    full_prompt = f"{system_prompt}\n\nContext:\n{chr(10).join(context)}\n\nPrompt: {prompt}"

    payload = {
        "model": MODEL,
        "prompt": full_prompt,
        "stream": False
    }

    try:
        response = requests.post(OLLAMA_API, json=payload, timeout=60)
        response.raise_for_status()
        data = response.json()
        return data.get("response", "")
    except requests.RequestException as e:
        console.print(f"[bold red]Error communicating with Ollama:[/] {e}")
        return ""

def extract_python_code(text: str) -> str:
    """Extracts Python code from Markdown code blocks."""
    match = re.search(r'```python\s*(.*?)\s*```', text, re.DOTALL)
    if match:
        return match.group(1)

    # Fallback if they didn't use the 'python' label
    match = re.search(r'```\s*(.*?)\s*```', text, re.DOTALL)
    if match:
        return match.group(1)

    return text.strip() # return everything if no blocks found

def execute_code(code: str) -> tuple[bool, str]:
    """Saves code to a temporary file and executes it. Returns (success, output)."""
    with open("temp_script.py", "w") as f:
        f.write(code)

    try:
        result = subprocess.run(["python3", "temp_script.py"], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
             return True, result.stdout
        else:
             return False, f"Error:\n{result.stderr}\nOutput:\n{result.stdout}"
    except Exception as e:
        return False, str(e)


def main():
    if len(sys.argv) < 2:
        console.print("[bold red]Usage:[/] python conjurer.py '<prompt>'")
        sys.exit(1)

    user_prompt = sys.argv[1]
    console.print(f"[bold blue]Conjuring code for:[/] {user_prompt}")

    context = []

    for attempt in range(MAX_RETRIES):
        console.print(f"\n[bold yellow]Attempt {attempt + 1}/{MAX_RETRIES}[/]")

        # Generate code
        response_text = generate_code(user_prompt, context)
        if not response_text:
             console.print("[bold red]Failed to get response from Ollama.[/]")
             break

        code = extract_python_code(response_text)

        console.print("[bold green]Generated Code:[/]")
        console.print(Markdown(f"```python\n{code}\n```"))

        # Execute code
        console.print("[bold cyan]Executing code...[/]")
        success, output = execute_code(code)

        if success:
             console.print(f"[bold green]Success![/]\n[bold]Output:[/]\n{output}")

             with open("conjured_script.py", "w") as f:
                 f.write(code)
             console.print("[bold magenta]Script saved as 'conjured_script.py'[/]")
             break
        else:
             console.print(f"[bold red]Execution Failed.[/]\n[bold]Error Output:[/]\n{output}")
             context.append(f"User Request: {user_prompt}")
             context.append(f"You generated:\n```python\n{code}\n```")
             context.append(f"Execution resulted in this error:\n{output}")
             context.append("Please fix the code and return the corrected Python script.")
             user_prompt = "Fix the error in the previous code."

    else:
         console.print("[bold red]Failed to conjure working code after max retries.[/]")

if __name__ == "__main__":
    main()
