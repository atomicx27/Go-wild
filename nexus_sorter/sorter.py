import os
import time
import shutil
import re
import requests
import json
from pathlib import Path
from rich.console import Console

console = Console()

INBOX_DIR = Path("nexus_sorter/inbox")
VAULT_DIR = Path("nexus_sorter/vault")
REJECTED_DIR = Path("nexus_sorter/rejected")
INDEX_FILE = VAULT_DIR / "INDEX.md"

INBOX_DIR.mkdir(parents=True, exist_ok=True)
VAULT_DIR.mkdir(parents=True, exist_ok=True)
REJECTED_DIR.mkdir(parents=True, exist_ok=True)
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "qwen2.5:0.5b"

SYSTEM_PROMPT = """You are an overworked, highly sarcastic, and cynical AI file clerk.
Your job is to read a snippet of a file and return ONLY a JSON object.
Do not add any markdown formatting, do not use ```json blocks, do not include any other text.
The JSON must have the following keys:
- "new_filename": A creative, descriptive name for the file (keep the original extension if present, otherwise guess it).
- "category": A broad category for this file (e.g., "Code", "Data", "Random_Junk").
- "summary": A one-sentence summary of what the file is.
- "roast": A snarky, cynical roast of the file's contents or the person who wrote it.

Example output:
{
  "new_filename": "terrible_python_script.py",
  "category": "Code",
  "summary": "A python script that prints hello world.",
  "roast": "Wow, another hello world script. Did it take you all day to write this masterpiece?"
}
"""

def generate_ollama_response(prompt_text):
    try:
        response = requests.post(OLLAMA_URL, json={
            "model": MODEL_NAME,
            "prompt": prompt_text,
            "system": SYSTEM_PROMPT,
            "stream": False
        }, timeout=30)
        response.raise_for_status()
        return response.json().get("response", "")
    except Exception as e:
        console.print(f"[bold red]Error communicating with Ollama: {e}[/bold red]")
        return None

def process_file(filepath):
    console.print(f"[bold blue]Processing {filepath.name}...[/bold blue]")
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read(2000)
    except Exception as e:
        console.print(f"[bold red]Could not read {filepath.name}: {e}. Moving to rejected.[/bold red]")
        shutil.move(str(filepath), REJECTED_DIR / filepath.name)
        return

    prompt = f"File snippet:\n\n{content}\n\nReturn the JSON."
    response_text = generate_ollama_response(prompt)

    if not response_text:
        shutil.move(str(filepath), REJECTED_DIR / filepath.name)
        return

    # Robust regex fallback parsing
    new_filename = filepath.name
    category = "Unsorted"
    summary = "Failed to parse summary."
    roast = "The AI was too confused to even roast this."

    try:
        # try standard json parsing first
        data = json.loads(response_text)
        new_filename = data.get("new_filename", new_filename)
        category = data.get("category", category)
        summary = data.get("summary", summary)
        roast = data.get("roast", roast)
    except json.JSONDecodeError:
        console.print("[yellow]Failed to parse JSON, falling back to regex...[/yellow]")
        # fallback parsing
        filename_match = re.search(r'"new_filename"\s*:\s*"([^"]+)"', response_text)
        if filename_match: new_filename = filename_match.group(1)

        category_match = re.search(r'"category"\s*:\s*"([^"]+)"', response_text)
        if category_match: category = category_match.group(1)

        summary_match = re.search(r'"summary"\s*:\s*"([^"]+)"', response_text)
        if summary_match: summary = summary_match.group(1)

        roast_match = re.search(r'"roast"\s*:\s*"([^"]+)"', response_text)
        if roast_match: roast = roast_match.group(1)

    # Sanitize category for directory name
    category_dir_name = re.sub(r'[^a-zA-Z0-9_-]', '_', category)
    target_dir = VAULT_DIR / category_dir_name
    target_dir.mkdir(parents=True, exist_ok=True)

    # Ensure new filename is safe
    safe_filename = re.sub(r'[^a-zA-Z0-9_.-]', '_', new_filename)
    target_path = target_dir / safe_filename

    # Handle collisions
    counter = 1
    while target_path.exists():
        stem = target_path.stem
        ext = target_path.suffix
        target_path = target_dir / f"{stem}_{counter}{ext}"
        counter += 1

    shutil.move(str(filepath), target_path)
    console.print(f"[bold green]Moved {filepath.name} to {target_path}[/bold green]")

    # Update INDEX.md
    with open(INDEX_FILE, "a", encoding="utf-8") as f:
        f.write(f"### {target_path.relative_to(VAULT_DIR)}\n")
        f.write(f"**Original Name:** {filepath.name}\n")
        f.write(f"**Summary:** {summary}\n")
        f.write(f"**AI Roast:** *{roast}*\n\n")

def main():
    console.print("[bold magenta]Nexus Sorter started. Watching inbox...[/bold magenta]")
    while True:
        for filepath in INBOX_DIR.iterdir():
            if filepath.is_file():
                try:
                    process_file(filepath)
                except Exception as e:
                    console.print(f"[bold red]Unexpected error processing {filepath.name}: {e}[/bold red]")
                    try:
                        shutil.move(str(filepath), REJECTED_DIR / filepath.name)
                    except Exception as move_err:
                        console.print(f"[bold red]Failed to move {filepath.name} to rejected: {move_err}[/bold red]")
        time.sleep(2)

if __name__ == "__main__":
    main()
