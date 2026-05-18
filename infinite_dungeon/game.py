import sys
import argparse
from rich.console import Console
from rich.panel import Panel
from engine import DungeonEngine

console = Console()

def display_status(state):
    status_text = f"[bold red]Health:[/bold red] {state['health']} | [bold blue]Inventory:[/bold blue] {', '.join(state['inventory'])}"
    console.print(Panel(status_text, title="[bold]Player Status[/bold]", expand=False))

def main(test_mode=False):
    console.print("[bold green]Welcome to the Infinite Dungeon![/bold green]")
    console.print("Powered by Ollama.\n")

    engine = DungeonEngine()

    if test_mode:
        console.print("[bold yellow]Running in test mode...[/bold yellow]")
        result = engine.process_action("look around")
        console.print(f"Test Action: look around")
        console.print(f"Narrative: {result.get('narrative')}")
        console.print("[bold green]Test completed successfully![/bold green]")
        return

    # Initial context
    console.print(Panel(f"[italic]{engine.state['location']}[/italic]", title="[bold]Starting Location[/bold]"))

    while True:
        display_status(engine.state)

        if engine.state['health'] <= 0:
            console.print("[bold red]You have succumbed to your wounds. GAME OVER.[/bold red]")
            break

        action = console.input("\n[bold cyan]What do you want to do? (type 'quit' to exit): [/bold cyan]")

        if action.lower() in ['quit', 'exit', 'q']:
            console.print("[yellow]You coward. You flee the dungeon.[/yellow]")
            break

        with console.status("[bold green]The Game Master is pondering...[/bold green]", spinner="dots"):
            result = engine.process_action(action)

        console.print("\n")
        console.print(Panel(f"[italic]{result['narrative']}[/italic]"))

        if result.get("item_gained"):
            console.print(f"[bold green]+ Found item:[/bold green] {result['item_gained']}")
        if result.get("item_lost"):
            console.print(f"[bold red]- Lost item:[/bold red] {result['item_lost']}")
        if result.get("health_change", 0) != 0:
            change = result['health_change']
            color = "green" if change > 0 else "red"
            sign = "+" if change > 0 else ""
            console.print(f"[bold {color}]Health {sign}{change}[/bold {color}]")

        console.print("\n" + "="*50 + "\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Infinite Dungeon AI text adventure.")
    parser.add_argument("--test", action="store_true", help="Run a quick test of the engine.")
    args = parser.parse_args()
    main(test_mode=args.test)
