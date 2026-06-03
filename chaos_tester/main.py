import argparse
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.text import Text
from chaos_engine import ChaosEngine

console = Console()

def print_header():
    title = Text("🔥 CHAOS TESTER 🔥", style="bold red on black", justify="center")
    subtitle = Text("Autonomous Chaos Engineering Agent", style="italic yellow", justify="center")
    console.print(Panel(Text.assemble(title, "\n", subtitle), border_style="red"))

def main():
    parser = argparse.ArgumentParser(description="Chaos Tester: Autonomous mutation testing and test augmentation.")
    parser.add_argument("target", type=str, help="Path to the target Python source file.")
    parser.add_argument("test", type=str, help="Path to the corresponding pytest file.")
    parser.add_argument("--iterations", type=int, default=1, help="Number of mutation iterations to run.")
    args = parser.parse_args()

    target_path = Path(args.target).resolve()
    test_path = Path(args.test).resolve()

    print_header()

    if not target_path.exists():
        console.print(f"[bold red]Error:[/] Target file {target_path} not found.")
        return
    if not test_path.exists():
        console.print(f"[bold red]Error:[/] Test file {test_path} not found.")
        return

    engine = ChaosEngine()

    console.print("[bold cyan]Connecting to Ollama...[/]")
    if not engine.test_connection():
        console.print("[bold red]Failed to connect to local Ollama instance at http://localhost:11434. Ensure Ollama is running and the 'llama3' model is pulled.[/]")
        return

    console.print("[bold green]Connection successful![/]\n")

    stats = {
        "killed": 0,
        "survived": 0,
        "tests_generated": 0
    }

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("[cyan]Running chaos iterations...", total=args.iterations)

        for i in range(args.iterations):
            progress.update(task, description=f"[cyan]Iteration {i+1}/{args.iterations}: Processing {target_path.name}...[/]")

            results = engine.process_target(target_path, test_path)

            if not results.get("initial_tests_passed"):
                progress.stop()
                console.print(f"\n[bold red]Iteration {i+1} Aborted:[/] Initial tests failed on the original code. Fix your tests first!")
                break

            if results.get("mutation_survived"):
                stats["survived"] += 1
                if results.get("new_test_passed"):
                    stats["tests_generated"] += 1
            else:
                stats["killed"] += 1

            progress.advance(task)

    # Print Report
    console.print("\n[bold magenta]=== Chaos Report ===[/]")
    console.print(f"Target: [yellow]{target_path.name}[/]")
    console.print(f"Iterations: [cyan]{args.iterations}[/]")
    console.print(f"Mutations Killed (Existing tests caught it): [green]{stats['killed']}[/]")
    console.print(f"Mutations Survived (Bug slipped through): [red]{stats['survived']}[/]")
    console.print(f"New Tests Successfully Generated & Added: [bold green]{stats['tests_generated']}[/]")

    if stats['survived'] > 0 and stats['tests_generated'] > 0:
         console.print("\n[bold green]Your test suite has been automatically strengthened![/]")
    elif stats['survived'] > 0 and stats['tests_generated'] == 0:
         console.print("\n[bold red]Bugs slipped through, but test generation failed. Review logs.[/]")
    else:
         console.print("\n[bold cyan]Your test suite is ironclad! No bugs survived.[/]")

if __name__ == "__main__":
    main()
