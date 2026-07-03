# DevCompanion

DevCompanion is a local, agentic AI assistant powered by Ollama. It can help you explore your system, write code, and execute bash commands directly from a terminal interface.

## Requirements

- Python 3.x
- Ollama running locally with the `qwen2.5-coder:1.5b` model pulled.
- See `requirements.txt` for Python dependencies.

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Ensure Ollama is running and the model is pulled:
   ```bash
   ollama pull qwen2.5-coder:1.5b
   ```

## Usage

Start the interactive session:
```bash
python3 main.py
```

You can chat with the assistant or ask it to perform system tasks. It will autonomously execute bash commands enclosed in `[CMD]...[/CMD]` blocks and analyze the output.
