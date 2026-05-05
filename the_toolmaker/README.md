# The Toolmaker

An autonomous agent that writes, saves, and executes its own Python tools on demand to solve user requests.

## How it Works

The Toolmaker is designed to be an expanding toolbox. When given a request, it follows these steps:

1. **Analyze:** It checks its `registry.json` to see if it has previously written a tool that can solve the current request.
2. **Forge:** If no suitable tool exists, it queries a local LLM (via Ollama) to write a new, self-contained Python script to solve the task. This script is saved in the `tools/` directory and added to the registry.
3. **Plan & Execute:** It asks the LLM for the exact bash command needed to run the chosen tool (existing or newly forged) with the correct arguments to fulfill the user's specific request, and then executes it.

This means The Toolmaker gets smarter over time. If you ask it to reverse a string once, it writes a string-reversing tool. The next time you ask it to reverse a string, it simply uses the tool it already wrote.

## Features

* **Zero Dependencies:** Written in pure Python, utilizing only the standard library (no `requests` or `langchain` required).
* **Local AI:** Connects to a local Ollama instance (`http://localhost:11434`).
* **Resilient:** Includes a fallback mock mechanism. If the Ollama server is unreachable, it will simulate responses, allowing the core application logic to be tested or run in constrained environments.

## Usage

### Direct Execution

Tell The Toolmaker to do something directly from the command line:

```bash
python main.py do "Create a tool that reverses a string and then run it on the string 'hello world'"
```

```bash
python main.py do "Check the current disk usage"
```

### Interactive REPL

Start a continuous loop where you can keep asking The Toolmaker to perform tasks:

```bash
python main.py interactive
```

Type `exit` or `quit` to leave the interactive mode.

## Project Structure

* `main.py`: The CLI entry point.
* `llm_logic.py`: Handles the core logic of analyzing requests, forging tools, and planning execution.
* `ollama_client.py`: A lightweight, standard-library-only wrapper for the Ollama API.
* `registry.py`: Manages the `registry.json` file to keep track of available tools.
* `tools/`: The directory where newly forged tools are saved.
