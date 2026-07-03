import requests
import json
import re
import subprocess
from rich.console import Console
from rich.markdown import Markdown
from prompt_toolkit import PromptSession

OLLAMA_API_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "qwen2.5-coder:1.5b"

console = Console()
session = PromptSession()

SYSTEM_PROMPT = """You are DevCompanion, a powerful, agentic AI assistant powered by Ollama.
You can help the user write code, explore files, and execute bash commands.

If you want to execute a bash command on the user's system to explore the environment or perform a task, use the following syntax:
[CMD]
<command>
[/CMD]

For example:
[CMD]
ls -la
[/CMD]

I will execute the command and provide you with the output in our conversation context. Only one [CMD] block per response is supported.
"""

def generate_response(prompt, context):
    payload = {
        "model": MODEL_NAME,
        "prompt": f"{SYSTEM_PROMPT}\n\nContext:\n{context}\n\nUser: {prompt}\nDevCompanion:",
        "stream": False
    }

    try:
        response = requests.post(OLLAMA_API_URL, json=payload)
        response.raise_for_status()
        return response.json().get("response", "")
    except requests.exceptions.RequestException as e:
        console.print(f"[bold red]Error communicating with Ollama: {e}[/bold red]")
        return ""

def execute_command(command):
    try:
        console.print(f"[bold yellow]Executing Command:[/bold yellow] {command}")
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=15)
        output = result.stdout + result.stderr
        console.print(f"[dim]{output}[/dim]")
        return f"Command Output:\n{output}"
    except subprocess.TimeoutExpired:
        return "Command Output:\nExecution timed out."
    except Exception as e:
        return f"Command Output:\nExecution failed: {e}"

def main():
    console.print(Markdown("# Welcome to DevCompanion"))
    console.print("[dim]Type 'quit' or 'exit' to leave.[/dim]\n")

    context = ""

    while True:
        try:
            user_input = session.prompt("You> ")
            if user_input.lower() in ['quit', 'exit']:
                break

            if not user_input.strip():
                continue

            with console.status("[bold green]Thinking..."):
                response_text = generate_response(user_input, context)

            console.print(Markdown(response_text))

            # Append user input and agent response to context FIRST
            context += f"User: {user_input}\nDevCompanion: {response_text}\n"

            # Check for command execution request
            cmd_match = re.search(r"\[CMD\]\s*(.*?)\s*\[/CMD\]", response_text, re.DOTALL)

            if cmd_match:
                command = cmd_match.group(1).strip()
                cmd_output = execute_command(command)

                # Feed output back to context
                context += f"System: Executed '{command}'. Output:\n{cmd_output}\n"

                # Ask agent to interpret output
                with console.status("[bold green]Analyzing output..."):
                    follow_up = generate_response("The command finished. What are your thoughts on the output?", context)
                    console.print(Markdown(follow_up))
                    # Add follow-up to context
                    context += f"DevCompanion (Follow-up): {follow_up}\n"

        except KeyboardInterrupt:
            continue
        except EOFError:
            break

if __name__ == "__main__":
    main()
