import requests
import json
import re
import subprocess
import os
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

console = Console()

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "qwen2.5:0.5b"

SYSTEM_PROMPT = """You are an AI system navigator and automation agent.
Your goal is to help the user achieve their task by executing bash commands on a Linux system.
Always provide the commands you want to execute inside a markdown bash code block.
For example:
```bash
ls -la
```
Only provide one bash block per response. Keep your explanations concise."""


def generate_response(prompt, context=None):
    """Generates a response from the Ollama model."""
    data = {
        "model": MODEL_NAME,
        "system": SYSTEM_PROMPT,
        "prompt": prompt,
        "stream": False
    }
    if context:
        data["context"] = context

    try:
        response = requests.post(OLLAMA_URL, json=data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        console.print(f"[bold red]Error communicating with Ollama:[/] {e}")
        return None

def extract_bash_script(text):
    """Extracts bash code from markdown blocks."""
    match = re.search(r'```bash\n(.*?)\n```', text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return None

def execute_command(command):
    """Executes a bash command and returns the output."""
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        return result.stdout, result.stderr, result.returncode
    except Exception as e:
         return "", str(e), 1

def main():
    console.print(Panel.fit("[bold blue]System Navigator AI Agent[/]\nType your task, or 'exit' to quit.", title="Welcome"))

    context = None

    while True:
        try:
            user_input = input("\n[You]> ")
            if user_input.lower() in ['exit', 'quit']:
                break

            if not user_input.strip():
                continue

            with console.status("[bold green]Thinking..."):
                response_data = generate_response(user_input, context)

            if not response_data:
                continue

            response_text = response_data.get("response", "")
            context = response_data.get("context", context)

            console.print(Panel(Markdown(response_text), title="Agent", border_style="green"))

            command = extract_bash_script(response_text)

            if command:
                console.print(Panel(command, title="Proposed Command", border_style="yellow"))
                confirm = input("Execute this command? (y/n): ")

                if confirm.lower() == 'y':
                    with console.status("[bold yellow]Executing..."):
                        stdout, stderr, returncode = execute_command(command)

                    output_text = f"Exit code: {returncode}\n"
                    if stdout:
                        output_text += f"\nStdout:\n{stdout}"
                    if stderr:
                        output_text += f"\nStderr:\n{stderr}"

                    console.print(Panel(output_text, title="Execution Result", border_style="magenta"))

                    # Feed the result back to the model as an automated message
                    feedback_prompt = f"The command was executed. Here is the output:\n{output_text}\nWhat should we do next?"
                    with console.status("[bold green]Analyzing result..."):
                         feedback_data = generate_response(feedback_prompt, context)

                    if feedback_data:
                         context = feedback_data.get("context", context)
                         console.print(Panel(Markdown(feedback_data.get("response", "")), title="Agent Follow-up", border_style="cyan"))

        except KeyboardInterrupt:
            break
        except Exception as e:
            console.print(f"[bold red]An error occurred:[/] {e}")

if __name__ == "__main__":
    main()
