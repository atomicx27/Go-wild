import sys
import subprocess
import requests
import json
import re
from rich.console import Console
from rich.panel import Panel

console = Console()

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "qwen2.5:0.5b"

SYSTEM_PROMPT = """You are System Healer, an autonomous AI agent capable of executing bash commands to achieve a specific goal.
You will be provided with a goal, and the output of the previous command you executed (if any).

Your task is to analyze the situation and provide the NEXT bash command to execute to get closer to the goal.

You must choose EXACTLY ONE of the following formats for your response:

Format 1 (if you need to run a command):
COMMAND: <the single bash command to execute>

Format 2 (if the goal is achieved and you are finished):
DONE

Do not output anything else. Do not provide explanations. Do not provide multiple commands.
"""

def query_ollama(goal, history):
    prompt = f"GOAL: {goal}\n\nHISTORY (Recent output):\n{history}\n\nWhat is the next command to execute? Remember to use 'COMMAND: <your command>' or 'DONE'. If you have already executed the command and it succeeded, output 'DONE'."

    data = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "system": SYSTEM_PROMPT,
        "stream": False,
        "options": {
            "temperature": 0.0 # Make it more deterministic
        }
    }

    try:
        response = requests.post(OLLAMA_URL, json=data, timeout=30)
        response.raise_for_status()
        response_json = response.json()
        return response_json.get("response", "")
    except requests.exceptions.RequestException as e:
        console.print(f"[bold red]Error communicating with Ollama: {e}[/bold red]")
        sys.exit(1)

def run_command(command):
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30
        )
        output = result.stdout + result.stderr
        returncode = result.returncode
        return output.strip(), returncode
    except subprocess.TimeoutExpired:
        return "Command timed out after 30 seconds.", -1
    except Exception as e:
        return f"Execution error: {e}", -1

def main():
    if len(sys.argv) < 2:
        console.print("[bold yellow]Usage: python system_healer.py '<your goal>'[/bold yellow]")
        sys.exit(1)

    goal = sys.argv[1]
    console.print(Panel(f"[bold green]GOAL: {goal}[/bold green]", title="System Healer Initialized"))

    history = "No commands executed yet."
    max_steps = 15
    step = 0
    executed_commands = set()

    while step < max_steps:
        step += 1
        console.print(f"\n[bold cyan]--- Step {step} ---[/bold cyan]")

        response = query_ollama(goal, history)

        if "DONE" in response and "COMMAND:" not in response:
            console.print(Panel("[bold green]Mission Accomplished! Agent reported DONE.[/bold green]"))
            sys.exit(0)

        match = re.search(r'COMMAND:\s*(.*)', response)
        if not match:
            # Let's try to extract any code block if it missed the formatting
            code_match = re.search(r'```(?:bash)?\n(.*?)```', response, re.DOTALL)
            if code_match:
                command = code_match.group(1).strip()
            else:
                console.print("[bold red]Failed to parse command from LLM response.[/bold red]")
                console.print(f"Raw response: {response}")
                history = f"Error: You did not output a command in the 'COMMAND: <cmd>' format. Raw output was: {response}"
                continue
        else:
            command = match.group(1).strip()

        # Clean up any trailing backticks from the command
        command = command.replace('```', '').strip()

        if command in executed_commands:
            console.print(f"[bold yellow]Agent tried to repeat command: {command}. Assuming DONE.[/bold yellow]")
            sys.exit(0)

        executed_commands.add(command)
        console.print(f"[bold magenta]Executing:[/bold magenta] {command}")

        output, returncode = run_command(command)

        if output:
            console.print(f"[dim]Output:\n{output[:500]}{'...' if len(output) > 500 else ''}[/dim]")
        else:
            console.print(f"[dim](No output)[/dim]")
            output = "(Command completed with no output)"

        history = f"Executed: {command}\nReturn Code: {returncode}\nOutput: {output}"

        if "DONE" in response:
             console.print(Panel("[bold green]Mission Accomplished! Agent reported DONE.[/bold green]"))
             sys.exit(0)

    console.print("\n[bold red]Max steps reached. The agent failed to achieve the goal in the allotted time.[/bold red]")
    sys.exit(1)

if __name__ == "__main__":
    main()
