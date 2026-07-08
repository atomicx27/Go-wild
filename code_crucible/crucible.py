import argparse
import importlib
import os
import re
import requests
import shutil
import sys
import tempfile
import timeit
import pytest

from rich.console import Console
from rich.table import Table

console = Console()

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "qwen2.5:0.5b"

PERSONAS = {
    "Speed Demon": "Optimize the following python code to run as fast as possible. Use any valid python tricks or libraries like `functools.lru_cache` if applicable. Return only the optimized python code in a markdown block.",
    "Code Golfer": "Refactor the following python code to be as short as possible (minimum number of characters), without losing functionality. Return only the golfed python code in a markdown block.",
    "Chaos Mage": "Rewrite the following python code using unconventional, bizarre, or overly complex but valid python techniques. Keep the function signature identical and ensure it still passes the tests. Return only the chaotic python code in a markdown block.",
    "Enterprise Architect": "Rewrite the following python code to be extremely verbose, using classes, type hints, and overly formal enterprise patterns. Keep the core function signature accessible. Return only the enterprise python code in a markdown block."
}

def prompt_ollama(prompt: str) -> str | None:
    """Prompt Ollama and return the text content."""
    try:
        response = requests.post(OLLAMA_URL, json={
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False
        }, timeout=60)
        response.raise_for_status()
        return response.json().get("response")
    except requests.exceptions.RequestException as e:
        console.print(f"[red]Error communicating with Ollama: {e}[/red]")
        return None

def extract_code(text: str) -> str:
    """Extract python code from markdown block."""
    if not text:
        return ""
    match = re.search(r"```(?:python)?\n(.*?)```", text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return text.strip()

def run_tests_on_mutant(mutant_filepath: str, original_test_filepath: str, target_module: str) -> bool:
    """Run pytest on the mutant code."""
    # Create a temporary test file that imports from the mutant instead
    with open(original_test_filepath, "r") as f:
        test_content = f.read()

    # We assume the test file has `from {target_module} import ...` or `import {target_module}`
    # e.g., `from examples.fib import get_nth_fibonacci` -> `from arena.mutant_speed_demon import get_nth_fibonacci`

    mutant_module_path = mutant_filepath.replace(".py", "").replace(os.path.sep, ".")
    # We replace 'examples.fib' with 'arena.mutant_something'
    # Actually, we need a robust way. Let's just find `from {something}.{target_module} import` or `from {target_module} import`

    # Simple replacement: look for the target module name in imports and replace the path
    # Easiest way: modify PYTHONPATH to prioritize the arena directory? No, let's just use string replacement on the test.

    # Let's extract the base name of the mutant module
    mutant_module_name = os.path.basename(mutant_filepath).replace(".py", "")

    # e.g. "from examples.fib import" -> "from arena.mutant_speed_demon import"
    # Find the line doing the import and replace the module part.
    # We will assume a specific format for this example: `from examples.fib import`

    # A generic regex approach for imports targeting the target_module
    # `from .*fib import` -> `from arena.mutant_speed_demon import`
    import_pattern = rf"from .*{target_module} import"
    replacement = f"from arena.{mutant_module_name} import"

    modified_test_content = re.sub(import_pattern, replacement, test_content)

    # Check if `import ...fib` is used
    import_pattern2 = rf"import .*{target_module}\b"
    replacement2 = f"import arena.{mutant_module_name} as {target_module}"
    modified_test_content = re.sub(import_pattern2, replacement2, modified_test_content)

    test_dir = os.path.dirname(original_test_filepath)
    if not test_dir:
        test_dir = "."
    temp_test_fd, temp_test_path = tempfile.mkstemp(suffix=".py", prefix="test_temp_", dir=test_dir)
    try:
        with os.fdopen(temp_test_fd, 'w') as f:
            f.write(modified_test_content)

        # Run pytest
        # capture output
        retcode = pytest.main([temp_test_path, "-q", "--disable-warnings"])
        return retcode == 0
    finally:
        if os.path.exists(temp_test_path):
            os.remove(temp_test_path)

def benchmark_mutant(mutant_filepath: str, benchmark_code: str) -> float:
    """Benchmark the mutant code using timeit."""
    mutant_module_name = os.path.basename(mutant_filepath).replace(".py", "")
    setup_code = f"from arena.{mutant_module_name} import *"

    try:
        # Run 1000 iterations
        time_taken = timeit.timeit(stmt=benchmark_code, setup=setup_code, number=1000)
        return time_taken
    except Exception as e:
        console.print(f"[yellow]Benchmark failed for {mutant_module_name}: {e}[/yellow]")
        return float('inf')


def main():
    parser = argparse.ArgumentParser(description="Code Crucible - Mutate and benchmark code with Ollama.")
    parser.add_argument("--file", required=True, help="Target python file to mutate.")
    parser.add_argument("--test", required=True, help="Test file for the target code.")
    parser.add_argument("--target-module", required=True, help="Module name of the target code (e.g., 'fib' for 'fib.py').")
    parser.add_argument("--benchmark", required=True, help="Python code snippet to run for benchmarking (e.g., 'get_nth_fibonacci(20)').")
    args = parser.parse_args()

    target_file = args.file
    test_file = args.test
    target_module = args.target_module
    benchmark_snippet = args.benchmark

    if not os.path.exists(target_file):
        console.print(f"[red]Target file {target_file} not found.[/red]")
        sys.exit(1)

    if not os.path.exists(test_file):
        console.print(f"[red]Test file {test_file} not found.[/red]")
        sys.exit(1)

    with open(target_file, "r") as f:
        original_code = f.read()

    os.makedirs("arena", exist_ok=True)

    results = []

    # Benchmark original
    console.print("[cyan]Running original code benchmark...[/cyan]")
    original_module_path = target_file.replace(".py", "").replace(os.path.sep, ".")
    # create a dummy link in arena so it can be benchmarked same way or just benchmark directly
    shutil.copy(target_file, os.path.join("arena", "mutant_original.py"))
    original_time = benchmark_mutant(os.path.join("arena", "mutant_original.py"), benchmark_snippet)
    original_size = len(original_code)
    results.append({
        "Persona": "Original",
        "Status": "Passed",
        "Time (s)": original_time,
        "Size (chars)": original_size
    })

    for persona_name, persona_prompt in PERSONAS.items():
        console.print(f"\n[bold magenta]Summoning {persona_name}...[/bold magenta]")
        full_prompt = f"{persona_prompt}\n\n```python\n{original_code}\n```"

        response_text = prompt_ollama(full_prompt)
        if not response_text:
            continue

        mutated_code = extract_code(response_text)

        safe_persona_name = persona_name.lower().replace(" ", "_")
        mutant_filepath = os.path.join("arena", f"mutant_{safe_persona_name}.py")

        with open(mutant_filepath, "w") as f:
            f.write(mutated_code)

        console.print(f"Generated mutant saved to [yellow]{mutant_filepath}[/yellow].")

        console.print("Running tests...")
        passed = run_tests_on_mutant(mutant_filepath, test_file, target_module)

        if passed:
            console.print("[green]Tests passed![/green] Benchmarking...")
            time_taken = benchmark_mutant(mutant_filepath, benchmark_snippet)
            size = len(mutated_code)
            results.append({
                "Persona": persona_name,
                "Status": "Passed",
                "Time (s)": time_taken,
                "Size (chars)": size
            })
        else:
            console.print("[red]Tests failed! Mutant discarded.[/red]")
            results.append({
                "Persona": persona_name,
                "Status": "Failed",
                "Time (s)": "-",
                "Size (chars)": len(mutated_code)
            })

    # Print Results
    table = Table(title="Code Crucible Results")
    table.add_column("Persona", style="cyan")
    table.add_column("Status", style="magenta")
    table.add_column("Time (s)", justify="right", style="green")
    table.add_column("Size (chars)", justify="right", style="yellow")

    for res in results:
        time_str = f"{res['Time (s)']:.5f}" if isinstance(res["Time (s)"], float) else str(res["Time (s)"])
        status_color = "green" if res["Status"] == "Passed" else "red"
        table.add_row(res["Persona"], f"[{status_color}]{res['Status']}[/]", time_str, str(res["Size (chars)"]))

    console.print("\n")
    console.print(table)


if __name__ == "__main__":
    main()
