# Neuro-Mentor

An autonomous, agentic instructional designer and Cyberpunk-themed AI tutor powered by a local Ollama instance.

## Concept
Neuro-Mentor acts as a local data processor and interactive learning platform. Drop raw text notes, documentation, or study materials into the `inbox/` directory. A background agent automatically detects the new file, uses Ollama (`llama3`) to analyze the text, and structures it into a comprehensive "Learning Module."

This module includes:
- A catchy title and summary.
- A set of Flashcards to test your knowledge.
- A Multiple-Choice Quiz.
- A unique "Cyberpunk Tutor Persona" tailored to the subject matter.

Once processed, the module is available on the Cyberpunk Web UI, where you can interact with the study materials and chat live with the custom AI Tutor Persona to dive deeper into the topic.

## Features
- **Autonomous Agent**: Background watcher automatically parses text files dropped into the inbox without manual intervention.
- **Dynamic Content Generation**: Auto-generates flashcards, quizzes, and summaries from raw text.
- **Immersive Cyberpunk UI**: Features a dark-mode, CRT-styled interface with neon glows, tabbed navigation, and interactive 3D flashcards.
- **AI Persona Chat**: Engage in real-time conversation with a customized, themed AI tutor for an interactive learning experience.

## Installation

1. Navigate to the project directory:
   ```bash
   cd neuro_mentor
   ```

2. (Optional) Create a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Ensure Ollama is running locally on port 11434 with `llama3` installed.

## Usage

Start the FastAPI application (this also launches the background agent):
```bash
uvicorn main:app --reload
```

1. Open `http://localhost:8000` in your browser.
2. Drop a `.txt` file containing your study notes into the `neuro_mentor/inbox/` directory.
3. Wait a few moments. The agent will process the file, move the raw file to `processed/`, and generate a JSON engram in `data/`.
4. The Web UI will automatically update with the new module. Click it to begin learning!
