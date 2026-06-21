from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.text import Text
from rich.syntax import Syntax
from rich.live import Live
from rich.spinner import Spinner
from agent import OllamaAgent
import os

console = Console()

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def draw_header():
    title = Text("=== CODE SAVANT ===", style="bold bright_cyan")
    subtitle = Text("Autonomous Code Synthesizer v1.0", style="italic bright_magenta")
    panel = Panel(
        Text.assemble(title, "\n", subtitle, justify="center"),
        border_style="bright_blue",
        padding=(1, 2)
    )
    console.print(panel)

def main():
    clear_screen()
    draw_header()

    agent = OllamaAgent()

    while True:
        try:
            prompt = Prompt.ask("[bold bright_green]> Enter Task[/bold bright_green] ")

            if prompt.lower() in ['exit', 'quit']:
                console.print("[bold bright_red]Disconnecting from Code Savant...[/bold bright_red]")
                break

            if not prompt.strip():
                continue

            with console.status("[bold bright_yellow]Synthesizing and Validating Code...[/bold bright_yellow]", spinner="dots4"):
                result = agent.execute_and_heal(prompt)

            if result.get("success"):
                console.print(Panel(Syntax(result["code"], "python", theme="monokai", line_numbers=True), title="[bold bright_green]GENERATED CODE[/bold bright_green]", border_style="bright_green"))
                console.print(f"[bold bright_cyan]Attempts:[/bold bright_cyan] {result['attempts']}")
                console.print(Panel(result["output"], title="[bold bright_white]EXECUTION OUTPUT[/bold bright_white]", border_style="bright_white"))
            else:
                console.print(Panel(Syntax(result["code"], "python", theme="monokai", line_numbers=True), title="[bold bright_red]FAILED CODE[/bold bright_red]", border_style="bright_red"))
                console.print(Panel(result["output"], title="[bold bright_red]FINAL ERROR[/bold bright_red]", border_style="bright_red"))

        except KeyboardInterrupt:
            console.print("\n[bold bright_red]Disconnecting from Code Savant...[/bold bright_red]")
            break
        except Exception as e:
            console.print(f"[bold red]System Error:[/bold red] {e}")

if __name__ == "__main__":
    main()
