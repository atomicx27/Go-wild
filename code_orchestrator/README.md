# Agentic Code Orchestrator 🚀

An intelligent code orchestration tool powered by Ollama and FastAPI. It runs locally and acts as an AI agent capable of breaking down prompts into executable plans and generating final implementations.

## Features

- **Local Execution:** Uses Ollama and `qwen2.5:0.5b` (or any other model you have pulled) for completely local processing.
- **Agentic Workflow:** The agent first outlines a step-by-step plan for your request before executing it.
- **FastAPI Backend:** Lightweight and efficient server for handling requests.
- **Web UI:** A clean, dark-mode web interface to interact with the agent.

## Getting Started

1. Ensure Ollama is running and you have pulled the model (`ollama pull qwen2.5:0.5b`).
2. Run the application:
   ```bash
   cd code_orchestrator
   source venv/bin/activate
   uvicorn app:app --host 0.0.0.0 --port 8000
   ```
3. Open your browser and navigate to `http://localhost:8000`.

## Built With
- FastAPI
- Ollama
- Jinja2 Templates
- Python
