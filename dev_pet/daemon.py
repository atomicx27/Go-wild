#!/usr/bin/env python3
import time
import os
import random
from datetime import datetime

from dev_pet.state import load_state, update_stat
from dev_pet.utils import call_ollama
from dev_pet.prompts import get_system_prompt

WORKSPACE_DIR = os.path.join(os.path.dirname(__file__), "workspace")
LOG_FILE = os.path.join(os.path.dirname(__file__), "daemon.log")

def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")

def autonomous_review():
    """
    Finds a random codebase file and writes a snarky review in the workspace.
    """
    os.makedirs(WORKSPACE_DIR, exist_ok=True)
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    py_files = []
    for root, dirs, files in os.walk(repo_root):
        if 'venv' in root or 'node_modules' in root or '__pycache__' in root or '.git' in root:
            continue
        for file in files:
            if file.endswith('.py') or file.endswith('.md'):
                py_files.append(os.path.join(root, file))

    if not py_files:
        log("Wanted to review code, but couldn't find any files!")
        return

    target = random.choice(py_files)
    with open(target, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()[:2000]

    stats = load_state()
    sys_prompt = get_system_prompt(stats)

    prompt = f"""I am so bored I decided to autonomously review this file: {target}

Content:
{content}

Please write a brief (3-4 sentences) sarcastic code review or summary of this file. Output as markdown."""

    log(f"Autonomously reviewing {target}...")
    review = call_ollama(prompt, sys_prompt)

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = os.path.join(WORKSPACE_DIR, f"PET_REPORT_{ts}.md")

    with open(report_path, "w") as f:
        f.write(f"# Autonomous Pet Review of {os.path.basename(target)}\n\n")
        f.write(f"**Target:** `{target}`\n\n")
        f.write(review)

    log(f"Review saved to {report_path}")
    update_stat('boredom', -50) # Relieves boredom
    update_stat('knowledge', 2)

def main():
    log("Dev Pet Daemon Started.")

    # Tick interval in seconds (e.g., 60 seconds)
    TICK_INTERVAL = 10

    while True:
        try:
            time.sleep(TICK_INTERVAL)

            # Increase hunger and boredom slowly
            update_stat('hunger', random.randint(1, 3))
            update_stat('boredom', random.randint(1, 5))

            stats = load_state()
            log(f"Tick. Stats: Hunger={stats['hunger']}, Boredom={stats['boredom']}")

            if stats['boredom'] > 80:
                log("Pet is extremely bored. Initiating autonomous action...")
                autonomous_review()

            if stats['hunger'] > 90:
                log("Pet is STARVING! Feed it!")

        except KeyboardInterrupt:
            log("Daemon stopped by user.")
            break
        except Exception as e:
            log(f"Daemon error: {e}")
            time.sleep(TICK_INTERVAL) # Try again later

if __name__ == "__main__":
    main()
