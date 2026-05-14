# Infinite Dungeon

An infinite, AI-generated text adventure game powered by a local Ollama instance.

## Overview

The `infinite_dungeon` project turns an LLM into an intelligent Game Master. It maintains a state (health, inventory, location, history) and uses structured JSON output to parse the results of your free-form actions. You can try any action, and the AI will dynamically determine the outcome, what items you find or lose, and how much damage you take.

## Requirements

- Python 3
- `requests`
- `rich`
- A local [Ollama](https://ollama.ai/) instance running on port 11434 with the `llama3` model installed.

## Setup

```bash
cd infinite_dungeon
pip install -r requirements.txt
```

## Running the Game

Start your local Ollama server, then run:

```bash
python3 game.py
```

To run a quick connection test:

```bash
python3 game.py --test
```
