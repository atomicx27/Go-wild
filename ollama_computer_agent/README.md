# Ollama Computer Agent

This is an agentic tool that connects to a local Ollama server running `llama3.2`.
It exposes tools to the LLM allowing it to interact directly with the computer system by executing bash commands and reading files.

## Prerequisites

- Ollama must be installed and running locally on port 11434.
- `llama3.2` model must be pulled (`ollama pull llama3.2`).

## Setup

```bash
pip install -r requirements.txt
```

## Usage

```bash
python agent.py
```

You can ask the agent to perform tasks such as "List the files in this directory" or "Read the file agent.py".
