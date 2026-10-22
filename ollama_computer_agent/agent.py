import requests
import json
import subprocess
from rich.console import Console
from rich.markdown import Markdown
from prompt_toolkit import PromptSession

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "llama3.2"

console = Console()

tools_definition = [
    {
        "type": "function",
        "function": {
            "name": "run_command",
            "description": "Executes a shell command. Use this to list files, modify files, run python scripts, run git commands, etc.",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {"type": "string", "description": "The bash command to run"}
                },
                "required": ["command"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Reads the contents of a file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filepath": {"type": "string", "description": "The path to the file"}
                },
                "required": ["filepath"]
            }
        }
    }
]

def run_command(command: str) -> str:
    try:
        console.print(f"[bold yellow]Executing:[/bold yellow] {command}")
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        out = result.stdout + result.stderr
        return out if out else "Command executed successfully with no output."
    except Exception as e:
        return f"Error executing command: {e}"

def read_file(filepath: str) -> str:
    try:
        console.print(f"[bold yellow]Reading:[/bold yellow] {filepath}")
        with open(filepath, 'r') as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {e}"

def chat_with_agent(messages):
    payload = {
        "model": MODEL,
        "messages": messages,
        "stream": False,
        "tools": tools_definition
    }

    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=60)
        response.raise_for_status()
        return response.json()["message"]
    except requests.exceptions.RequestException as e:
        console.print(f"[bold red]Error communicating with Ollama:[/bold red] {e}")
        return None

def main():
    console.print(f"[bold green]Welcome to the Ollama Computer Agent ({MODEL})![/bold green]")
    console.print("Type 'quit' or 'exit' to stop.")

    session = PromptSession()
    messages = [
        {"role": "system", "content": "You are a helpful assistant with access to tools. You can run bash commands and read files. If a user asks you to do something that requires a tool, use it. Do not guess file contents."}
    ]

    while True:
        try:
            user_input = session.prompt("\nYou: ")
            if user_input.lower() in ['quit', 'exit']:
                break
            if not user_input.strip():
                continue

            messages.append({"role": "user", "content": user_input})

            while True:
                assistant_message = chat_with_agent(messages)
                if not assistant_message:
                    break

                messages.append(assistant_message)

                if assistant_message.get("tool_calls"):
                    for tool_call in assistant_message["tool_calls"]:
                        func_name = tool_call["function"]["name"]
                        args = tool_call["function"]["arguments"]

                        result_content = ""
                        if func_name == "run_command":
                            result_content = run_command(args.get("command", ""))
                        elif func_name == "read_file":
                            result_content = read_file(args.get("filepath", ""))
                        else:
                            result_content = f"Unknown tool: {func_name}"

                        # Format as tool response per Ollama API spec
                        tool_msg = {
                            "role": "tool",
                            "content": result_content,
                            "name": func_name
                        }
                        messages.append(tool_msg)
                else:
                    # Final response
                    content = assistant_message.get("content", "")
                    if content:
                        console.print("\n[bold cyan]Agent:[/bold cyan]")
                        console.print(Markdown(content))
                    break

        except KeyboardInterrupt:
            continue
        except EOFError:
            break

if __name__ == "__main__":
    main()
