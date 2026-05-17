# App Smith (The Forge Master)

An autonomous agent that watches an inbox for app ideas and builds the full-stack application (HTML/JS/CSS/Python/etc.) using Ollama.

## How it works

1. Drop a text file with an application idea into the `inbox/` directory.
2. The `app_smith` daemon detects the new file.
3. It asks Ollama to design the architecture (file structure) of the application.
4. It iterates over the planned files, prompting Ollama to write the code for each.
5. The generated application is saved in the `outbox/<idea_name>/` directory.
6. The original idea text file is moved to the `processed/` directory.

## Setup

This project requires an active Ollama instance. By default, it connects to `http://localhost:11434`.

```bash
# Optional: Use a virtual environment
python3 -m venv venv
source venv/bin/activate

# Install requirements (none currently, just standard library!)
# pip install -r requirements.txt
```

## Running the Daemon

```bash
# Run continuously in the background
python3 app_smith.py

# Or run once and exit
python3 app_smith.py --run-once
```

## Configuration

You can override the default Ollama settings with environment variables:

*   `OLLAMA_URL`: Default is `http://localhost:11434/api/generate`
*   `OLLAMA_MODEL`: Default is `llama3.1` (You can change this to `codellama`, `mistral`, etc.)
