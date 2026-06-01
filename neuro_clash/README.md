# Neuro Clash

Neuro Clash is an autonomous, cyberpunk-themed debate arena powered by a local Ollama instance.

It orchestrates a debate between three distinct AI personas:
- **Moderator**: The objective, central arbiter who introduces the topic and concludes the debate.
- **Alpha**: A chaotic, rebellious hacker AI who debates with passion and slang.
- **Omega**: A cold, logical, corporate AI who debates with precision and formal language.

## Features
- **Cyberpunk UI**: A glowing, neon interface built with Tailwind CSS.
- **Autonomous Loop**: The frontend and backend communicate asynchronously to generate sequential debate turns.
- **Text-to-Speech**: Uses the browser's native Web Speech API to read the AI-generated responses aloud with varying pitch/rate to match character personas.
- **Local AI**: Fully powered by a local Ollama instance (defaulting to `llama3` or whatever model is available).

## Setup
1. Ensure Ollama is running locally on port 11434.
2. Create a virtual environment and install dependencies: `pip install -r requirements.txt`.
3. Run the FastAPI server: `uvicorn app:app --reload`.
4. Open the provided localhost URL (typically `http://127.0.0.1:8000/static/index.html`) in a modern browser.
