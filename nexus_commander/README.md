# Nexus Commander

Nexus Commander is a web-based, autonomous AI agent capable of executing bash commands to fulfill tasks directly on your machine. Powered locally by Ollama, it leverages a ReAct (Reasoning and Acting) loop to dynamically explore, execute, and solve problems.

## Features

- **Web UI**: A glowing, dark-themed, modern web interface to interact with the agent.
- **Agentic Loop**: Uses `<THINK>`, `<EXECUTE>`, and `<ANSWER>` logic to break down complex tasks.
- **Real-time Streaming**: Connects via WebSockets to stream the agent's thoughts and command execution outputs live to the browser.
- **Fully Local**: Relies on a local instance of Ollama (defaulting to the `llama3` model), ensuring complete privacy.

## Setup

1. Ensure Ollama is running locally on `http://localhost:11434` with the `llama3` model pulled (`ollama pull llama3`).
2. Navigate to the `nexus_commander` directory:
   ```bash
   cd nexus_commander
   ```
3. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Server

Start the FastAPI application:

```bash
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

Then, open your browser and navigate to `http://localhost:8000`.

## Testing

Run tests using pytest:

```bash
python3 -m pytest tests/
```
