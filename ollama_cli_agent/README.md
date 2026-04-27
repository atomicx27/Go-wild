# Ollama CLI Agent

An autonomous, command-line AI assistant powered by local LLMs via Ollama. It utilizes a ReAct (Reasoning and Acting) loop to dynamically execute shell commands on your machine to fulfill requests.

## Features

- **Agentic Capability**: Instead of just answering questions, the agent can execute real bash commands to find information, manipulate files, or automate tasks.
- **Local & Private**: Powered by Ollama, meaning all interactions and command reasoning run entirely on your local machine.
- **Beautiful UI**: Uses `rich` to provide a clean, color-coded terminal interface showing the agent's thought process, commands executed, and final answers.
- **Context Aware**: Captures standard output and standard error from commands and feeds them back into the agent's context.

## Prerequisites

1.  **Ollama**: Must be installed and running locally on `http://localhost:11434`.
2.  **Model**: A model must be pulled (defaults to `llama3`). You can pull it using `ollama pull llama3`.
3.  **Python**: Python 3.8+ required.

## Installation

1. Navigate to the project directory:
   ```bash
   cd ollama_cli_agent
   ```
2. Create a virtual environment (recommended):
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Start the agent:

```bash
python -m ollama_cli_agent.agent
```

You can then give it tasks, such as:
- *"What files are in the current directory?"*
- *"Find the largest file in my Downloads folder."*
- *"Create a new python script that calculates the fibonacci sequence."*

## How it works

The agent is given a strict system prompt instructing it to output specific XML tags:
- `<THINK>...</THINK>`: The agent's internal reasoning.
- `<EXECUTE>...</EXECUTE>`: A shell command it wants to run.
- `<ANSWER>...</ANSWER>`: The final response returned to the user once it has finished its task.

The Python loop parses these tags, executes the commands using `subprocess`, and feeds the output back into the conversation history until the agent provides a final `<ANSWER>`.
