# Code Metropolis

An autonomous agent that reads a codebase using Ollama to categorize files and generate a stunning interactive 3D Cyberpunk city visualization where each file is a building.

## Features

- **Agentic Analysis**: Scans your directory, filtering out cache and build folders.
- **Ollama Integration**: Uses a local `llama3` model to read the content of each file, categorize its purpose (UI, DB, LOGIC, etc.), estimate its complexity, and write a summary.
- **3D Visualization**: Renders a glowing neon city using `Three.js` and `EffectComposer` for bloom effects.
- **Interactive UI**: Hover over buildings to see them pulse. Click to reveal an overlay (styled with Tailwind CSS) showing the Ollama-generated analysis.

## Usage

Ensure you have Ollama running locally (`http://localhost:11434`) with the `llama3` model pulled (`ollama pull llama3`).

Run the server and point it to a directory you want to analyze (defaults to the current directory).

```bash
cd code_metropolis
python server.py /path/to/some/codebase
```

Then open `http://localhost:8000` in your web browser.

*Note: The first time it runs on a large codebase, it may take a few moments for the agent to query Ollama for every file. If Ollama is unreachable, the agent falls back to generating placeholder structural data so you can still view the city.*