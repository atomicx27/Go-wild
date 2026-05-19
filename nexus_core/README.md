# Nexus Core

Nexus Core is an autonomous multi-purpose agent core featuring a modern cyberpunk Web UI, utilizing a ReAct agent loop powered by a local Ollama instance.

## Features
- **ReAct Loop:** Analyzes tasks, reasons about them, executes tools, and evaluates results.
- **Tools:** The agent can write files, read files, list files, and evaluate Python code securely within its designated `workspace/` directory.
- **Mock Mode Fallback:** If Ollama is not detected, Nexus Core gracefully falls back to a mock simulation mode so the Web UI functionality remains demonstrable.
- **Cyberpunk UI:** Modern glassmorphism, neon effects, pulsing status indicators, and an auto-scrolling live terminal for observing the agent's thought process.
- **Zero Dependencies:** The backend relies entirely on the Python Standard Library (e.g. `http.server`, `urllib.request`).

## Setup & Running

1. Ensure Python 3.8+ is installed.
2. Ensure [Ollama](https://ollama.com/) is running locally with the `llama3` model pulled (`ollama run llama3`).
   *Note: If Ollama is not running, the application will still launch and use a mock agent simulation.*
3. Run the standalone server from the root of the repository:

```bash
python -m nexus_core.server
```

4. Open your browser and navigate to `http://localhost:8000`.
5. Enter a command in the interface and watch the agent work!