import os
import sys
import subprocess
import time
import requests
import json
import tempfile
from rich.console import Console

console = Console()
OLLAMA_API = "http://localhost:11434/api/generate"
MODEL = "qwen2.5-coder:1.5b"

def query_ollama(prompt: str) -> str:
    """Queries Ollama and extracts the python block."""
    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False
    }
    try:
        response = requests.post(OLLAMA_API, json=payload, timeout=60)
        response.raise_for_status()
        output = response.json().get("response", "")

        # Extract python code block
        if "```python" in output:
            code = output.split("```python")[1].split("```")[0].strip()
            return code
        elif "```" in output:
             code = output.split("```")[1].split("```")[0].strip()
             return code
        return output.strip()
    except Exception as e:
        console.print(f"[red]Error querying Ollama: {e}[/red]")
        return ""

def generate_api_code(description: str) -> str:
    prompt = f"""
You are an expert Python API developer. Write a fully self-contained FastAPI application in a single file based on this description:
"{description}"

Requirements:
- Use FastAPI.
- Include Pydantic models for data validation.
- Implement in-memory CRUD operations (Create, Read, Update, Delete) using a dictionary or list.
- Add some mock seed data so GET requests return something immediately.
- The code must run when executed directly using `if __name__ == "__main__": uvicorn.run(app, host="0.0.0.0", port=8000)`.

Return ONLY the raw python code in a markdown block. Do not include any explanations.
    """
    console.print("[cyan]Querying Ollama for initial API code...[/cyan]")
    return query_ollama(prompt)

def fix_code(code: str, error_message: str) -> str:
    prompt = f"""
The following FastAPI code crashed or encountered an error.

Error Message:
{error_message}

Code:
```python
{code}
```

Fix the code so it runs without errors.
Return ONLY the full corrected python code in a markdown block. Do not include any explanations.
    """
    console.print("[yellow]Querying Ollama to fix the code...[/yellow]")
    return query_ollama(prompt)

def test_and_heal(filepath: str, max_retries: int = 3):
    """Launches the app, tests it, and uses Ollama to fix errors if it crashes."""
    for attempt in range(max_retries):
        console.print(f"[bold magenta]Attempt {attempt + 1} / {max_retries}[/bold magenta]")

        # Start the server process
        process = subprocess.Popen(
            [sys.executable, filepath],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        # Wait a bit for the server to start
        time.sleep(3)

        # Check if process crashed immediately
        if process.poll() is not None:
            stdout, stderr = process.communicate()
            error_msg = stderr or stdout
            if not error_msg:
                # If there's no output and it exited immediately, it probably missed the uvicorn.run call
                error_msg = "The application exited immediately without starting the server. Did you include `if __name__ == '__main__': uvicorn.run(app, host='0.0.0.0', port=8000)` at the bottom of the file? Also make sure to import uvicorn."
            console.print(f"[red]Server crashed on startup. Error:[/red]\n{error_msg}")

            with open(filepath, "r") as f:
                current_code = f.read()

            new_code = fix_code(current_code, error_msg)
            if new_code:
                 with open(filepath, "w") as f:
                     f.write(new_code)
                 continue # Try again
            else:
                 console.print("[red]Failed to get fixed code from Ollama.[/red]")
                 break

        # If it didn't crash, try to make a request
        try:
            res = requests.get("http://127.0.0.1:8000/docs", timeout=5)
            if res.status_code == 200:
                console.print("[green]Server is running and /docs is accessible![/green]")
                process.terminate()
                return True
            else:
                 error_msg = f"HTTP Error: Expected 200, got {res.status_code}"
                 console.print(f"[red]{error_msg}[/red]")
        except requests.exceptions.RequestException as e:
            error_msg = f"Request failed: {e}"
            console.print(f"[red]{error_msg}[/red]")

            # Check logs to see if it crashed during the request
            if process.poll() is not None:
                stdout, stderr = process.communicate()
                error_msg += f"\nServer Output: {stderr or stdout}"

        # If we got here, there was an issue with the request or it crashed during request
        process.terminate()
        with open(filepath, "r") as f:
            current_code = f.read()

        new_code = fix_code(current_code, error_msg)
        if new_code:
             with open(filepath, "w") as f:
                 f.write(new_code)
        else:
             console.print("[red]Failed to get fixed code from Ollama.[/red]")
             break

    console.print("[bold red]Failed to create a working API after maximum retries.[/bold red]")
    return False

def build_api(description: str, output_file: str = "app.py"):
    # 1. Generate initial code
    code = generate_api_code(description)
    if not code:
        console.print("[red]Failed to generate initial code.[/red]")
        return

    with open(output_file, "w") as f:
        f.write(code)

    console.print(f"[green]Initial code saved to {output_file}[/green]")

    # 2. Enter self-healing loop
    success = test_and_heal(output_file)
    if success:
        console.print(f"[bold green]Successfully forged and verified {output_file}![/bold green]")
        console.print(f"[cyan]You can now run it with: python3 {output_file}[/cyan]")
