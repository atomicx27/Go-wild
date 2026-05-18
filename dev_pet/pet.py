#!/usr/bin/env python3
import sys
import os
import glob
import random
from dev_pet.state import load_state, update_stat
from dev_pet.utils import call_ollama
from dev_pet.prompts import get_ascii_art, get_system_prompt

def cmd_status():
    stats = load_state()
    print(get_ascii_art(stats))
    print("=== DEV PET STATUS ===")
    print(f"Hunger:    {'#' * (stats['hunger'] // 10):<10} ({stats['hunger']}/100)")
    print(f"Boredom:   {'#' * (stats['boredom'] // 10):<10} ({stats['boredom']}/100)")
    print(f"Knowledge: {stats['knowledge']}")
    print("======================")

    sys_prompt = get_system_prompt(stats)
    thought = call_ollama("Give me a brief, one-sentence thought about your current status.", sys_prompt)
    print(f"\nPet says: \"{thought.strip()}\"")

def cmd_feed(filepath):
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return

    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()[:2000] # Feed a chunk

    stats = load_state()
    sys_prompt = get_system_prompt(stats)
    prompt = f"I am feeding you this file: {filepath}\n\nContent:\n{content}\n\nGive me a 1-sentence summary of what you 'ate'."

    response = call_ollama(prompt, sys_prompt)
    print(get_ascii_art(stats))
    print(f"Pet says: \"{response.strip()}\"")

    update_stat('hunger', -30)
    update_stat('knowledge', 1)
    print("\n* Your pet's hunger decreased by 30! *")

def cmd_play():
    # Find a random python file in the parent dir (repo root) to 'play' with
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    py_files = []
    for root, dirs, files in os.walk(repo_root):
        if 'venv' in root or 'node_modules' in root or '__pycache__' in root:
            continue
        for file in files:
            if file.endswith('.py'):
                py_files.append(os.path.join(root, file))

    if not py_files:
        print("Couldn't find any .py files to play with!")
        return

    random_file = random.choice(py_files)
    with open(random_file, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()[:2000]

    stats = load_state()
    sys_prompt = get_system_prompt(stats)
    prompt = f"Let's play! Look at this code from {os.path.basename(random_file)}:\n\n{content}\n\nGive me one fun, weird, or snarky suggestion on how to improve or break it."

    response = call_ollama(prompt, sys_prompt)
    print(get_ascii_art(stats))
    print(f"Pet says: \"{response.strip()}\"")

    update_stat('boredom', -40)
    print("\n* Your pet's boredom decreased by 40! *")

def cmd_chat(message):
    stats = load_state()
    sys_prompt = get_system_prompt(stats)
    response = call_ollama(message, sys_prompt)
    print(get_ascii_art(stats))
    print(f"Pet says: \"{response.strip()}\"")

def main():
    if len(sys.argv) < 2:
        print("Usage: python pet.py [status|feed <file>|play|chat <message>]")
        sys.exit(1)

    command = sys.argv[1].lower()

    if command == "status":
        cmd_status()
    elif command == "feed":
        if len(sys.argv) < 3:
            print("Usage: python pet.py feed <file_path>")
        else:
            cmd_feed(sys.argv[2])
    elif command == "play":
        cmd_play()
    elif command == "chat":
        if len(sys.argv) < 3:
            print("Usage: python pet.py chat <message>")
        else:
            cmd_chat(" ".join(sys.argv[2:]))
    else:
        print(f"Unknown command: {command}")

if __name__ == "__main__":
    main()
