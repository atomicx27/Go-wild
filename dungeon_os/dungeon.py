import os
import json
import requests
import sys
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.prompt import Prompt
from rich.text import Text

console = Console()
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "qwen2.5:7b"

def ask_ollama(prompt, system_prompt="You are a Dungeon Master for a text-based RPG. Keep it concise, atmospheric, and imaginative."):
    data = {
        "model": MODEL,
        "prompt": prompt,
        "system": system_prompt,
        "stream": False
    }
    try:
        response = requests.post(OLLAMA_URL, json=data, timeout=15)
        response.raise_for_status()
        return response.json().get("response", "The magic fizzles...").strip()
    except Exception as e:
        return f"A magical disruption prevents you from seeing clearly: {e}"

def describe_room(path):
    dirs = []
    files = []
    try:
        for item in os.listdir(path):
            if os.path.isdir(os.path.join(path, item)):
                dirs.append(item)
            else:
                files.append(item)
    except PermissionError:
        return "A magical ward prevents you from seeing further into this room."

    prompt = f"I am in a dungeon room called '{os.path.basename(path) or '/'}'. I see doors leading to: {', '.join(dirs) if dirs else 'nowhere'}. Scattered on the floor are items: {', '.join(files) if files else 'nothing'}. Describe this room in a dark fantasy RPG style (2-3 sentences max). Do not list the items or doors explicitly, just weave them into the description."
    return ask_ollama(prompt)

def inspect_item(filepath):
    if not os.path.exists(filepath):
        return "That item doesn't exist here."

    size = os.path.getsize(filepath)
    ext = os.path.splitext(filepath)[1]

    prompt = f"I found a magical item. It is called '{os.path.basename(filepath)}', its size is {size} bytes, and it is a '{ext}' type. Describe what it looks like and what magical properties it might hold in a fantasy setting (2 sentences max)."
    return ask_ollama(prompt)

def get_advice(path, question):
    items = os.listdir(path)
    prompt = f"I am an adventurer in a dungeon room with these items/paths: {', '.join(items)}. I ask my spectral companion: '{question}'. How does the companion reply based on our surroundings? (Keep it short, 1-2 sentences)."
    return ask_ollama(prompt, system_prompt="You are a helpful but slightly sarcastic spectral companion to an adventurer.")

def print_ui(path, description):
    dirs = [d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))]
    files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]

    console.clear()

    header = Text(f" DungeonOS: {os.path.abspath(path)} ", style="bold white on blue")
    console.print(header)

    console.print(Panel(description, title="Room Description", border_style="cyan"))

    if dirs:
        dir_text = Text(", ".join(dirs), style="bold yellow")
        console.print(Panel(dir_text, title="Doors (go <name>)", border_style="yellow"))

    if files:
        file_text = Text(", ".join(files), style="bold green")
        console.print(Panel(file_text, title="Items (inspect <name>)", border_style="green"))

def main():
    current_path = os.getcwd()

    while True:
        try:
            desc = describe_room(current_path)
            print_ui(current_path, desc)

            cmd_input = Prompt.ask("\n[bold red]What do you do?[/bold red]")
            parts = cmd_input.strip().split(" ", 1)
            cmd = parts[0].lower()
            arg = parts[1] if len(parts) > 1 else ""

            if cmd in ["quit", "exit"]:
                console.print("[bold red]You leave the dungeon.[/bold red]")
                break

            elif cmd == "look":
                continue # The loop will re-describe the room

            elif cmd == "go" or cmd == "cd":
                if not arg:
                    console.print("[red]Go where?[/red]")
                    Prompt.ask("Press Enter to continue")
                    continue

                target = os.path.join(current_path, arg)
                if os.path.isdir(target):
                    current_path = os.path.abspath(target)
                else:
                    console.print(f"[red]There is no door called '{arg}'.[/red]")
                    Prompt.ask("Press Enter to continue")

            elif cmd == "inspect":
                if not arg:
                    console.print("[red]Inspect what?[/red]")
                    Prompt.ask("Press Enter to continue")
                    continue

                target = os.path.join(current_path, arg)
                if os.path.isfile(target):
                    with console.status(f"[bold green]Inspecting {arg}..."):
                        item_desc = inspect_item(target)
                    console.print(Panel(item_desc, title=f"Inspecting: {arg}", border_style="magenta"))
                    Prompt.ask("Press Enter to continue")
                else:
                    console.print(f"[red]There is no item called '{arg}'.[/red]")
                    Prompt.ask("Press Enter to continue")

            elif cmd == "ask":
                if not arg:
                    console.print("[red]Ask what?[/red]")
                    Prompt.ask("Press Enter to continue")
                    continue
                with console.status("[bold blue]Consulting your spectral companion..."):
                    advice = get_advice(current_path, arg)
                console.print(Panel(advice, title="Spectral Companion", border_style="blue"))
                Prompt.ask("Press Enter to continue")

            else:
                console.print(f"[red]Unknown action: {cmd}[/red]")
                console.print("Try: [yellow]look, go <door>, inspect <item>, ask <question>, quit[/yellow]")
                Prompt.ask("Press Enter to continue")

        except (KeyboardInterrupt, EOFError):
            break

if __name__ == "__main__":
    main()
