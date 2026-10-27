import sys
import os
from rich.console import Console
from rich.panel import Panel
from agent import build_api

console = Console()

def main():
    console.print(Panel.fit("[bold cyan]Welcome to Phantom Backend[/bold cyan]\n[green]The autonomous, self-healing API generator.[/green]"))

    if len(sys.argv) > 1:
        description = " ".join(sys.argv[1:])
    else:
        description = console.input("[bold yellow]Describe the API you want to build: [/bold yellow]")

    if not description.strip():
        console.print("[red]Description cannot be empty.[/red]")
        sys.exit(1)

    output_file = os.path.join(os.path.dirname(__file__), "app.py")

    console.print(f"\n[bold blue]Forging API for:[/bold blue] {description}\n")
    build_api(description, output_file)

if __name__ == "__main__":
    main()
