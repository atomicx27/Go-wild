# Self-Healing FastAPI Server

This project demonstrates a unique agentic workflow: a web server that fixes its own bugs in real-time.

## Concept

1. A user hits an endpoint that contains a bug (e.g., a `ZeroDivisionError`).
2. The server catches the unhandled exception using a custom `SelfHealingMiddleware`.
3. Instead of just returning a 500 error, it returns a 500 error *and* spins up a background task.
4. The background task (`healer.py`) analyzes the traceback, finds the source file, and sends the buggy code and the traceback to a local Ollama instance.
5. Ollama acts as a coding agent, figures out the fix, and returns a Git-style merge diff.
6. The server applies the patch to its own source code on disk.
7. (Assuming you run with something like `uvicorn --reload`), the server automatically restarts with the fixed code.
8. The next time the user hits the endpoint, it works perfectly.

## Files

- `main.py`: The FastAPI app and middleware.
- `buggy_routes.py`: Endpoints with intentional bugs.
- `healer.py`: The agentic logic that communicates with Ollama.
- `patcher.py`: Logic to safely apply git merge diffs to source files.
- `mock_ollama.py`: A mock server for testing without a real LLM.
- `run_demo.py`: An automated script that proves the concept works from end-to-end.

## Running the Demo (Mock Mode)

To see it in action without needing to install or configure Ollama:

```bash
cd self_healing_server
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python run_demo.py
```

## Running with Real Ollama

1. Ensure Ollama is running (`http://localhost:11434`).
2. Ensure you have pulled `llama3` (`ollama pull llama3`).
3. Start the server with uvicorn's reload flag so it picks up the patched files:
   ```bash
   uvicorn main:app --reload
   ```
4. Hit a buggy endpoint in your browser: `http://localhost:8000/divide?a=10&b=0`
5. Watch the server logs as it talks to Ollama, receives the patch, and reloads!