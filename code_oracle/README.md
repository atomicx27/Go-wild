# Code Oracle

Code Oracle is a pure Python, zero-dependency, local RAG (Retrieval-Augmented Generation) engine designed to let you chat with your entire codebase seamlessly using a local Ollama instance.

## Features

- **Blazing Fast Local Search**: Uses SQLite's FTS5 engine for incredibly fast full-text searching across your repository.
- **Local AI Powered**: Integrates with your local Ollama instance (e.g., `qwen2.5-coder:7b`) for privacy-first codebase analysis.
- **Cyberpunk UI**: A highly interactive, glowing glassmorphism web interface served via a pure Python server.
- **Streaming Responses**: Real-time response streaming for a smooth chat experience.
- **Zero Dependencies**: Everything is built using standard Python libraries (`sqlite3`, `http.server`, `urllib`).

## Setup & Usage

1. Ensure [Ollama](https://ollama.com/) is running locally on port 11434 with a suitable coder model. By default, it expects `qwen2.5-coder:7b`, but you can change this in `llm.py`.
2. Run the application from the repository root:

```bash
python -m code_oracle.main
```

3. The first run will automatically index your codebase into `code_index.db`.
4. Open your browser and navigate to `http://localhost:8080` to start querying the Code Oracle.
