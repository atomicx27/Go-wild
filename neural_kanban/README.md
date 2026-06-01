# Neural Kanban

An autonomous, local AI-powered Kanban project management board.

**Neural Kanban** watches for new tickets to be added to the board. Once a ticket is created, an autonomous background agent queries a local Ollama instance (using the `llama3` model by default) to act as a Project Manager or Tech Lead. The AI breaks down the task, offers boilerplate code or architectural advice, and posts it as a detailed, Markdown-formatted comment in the ticket.

## Features
- **Modern Cyberpunk UI**: Built with Tailwind CSS, featuring glassmorphism, glowing hover effects, and smooth drag-and-drop.
- **Autonomous Agent**: A background loop polls for new tickets and processes them via Ollama.
- **Markdown Comments**: AI analysis is formatted nicely in the UI using marked.js.
- **Zero-Dependency Agent**: The agent loop is pure Python (`asyncio` and `httpx`), directly integrated with the FastAPI lifespan.

## Requirements
- Python 3.9+
- A local [Ollama](https://ollama.ai/) instance running on `http://localhost:11434`
- The `llama3` model installed in Ollama (`ollama run llama3`)

## Installation & Running

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Start the FastAPI server (which automatically starts the AI agent loop):
   ```bash
   uvicorn backend.main:app --host 0.0.0.0 --port 8000
   ```

3. Open your browser to `http://localhost:8000`.

4. Click "+ New Ticket" and create a task. Wait a few seconds for the AI to analyze it, then click "View ->" to see the Neural PM's breakdown!
