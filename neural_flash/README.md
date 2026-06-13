# Neural Flash

An autonomous, Ollama-powered flashcard generator and Leitner system review web application with a cyberpunk aesthetic.

## Features
- **Autonomous Agent Generation**: Drop a text file in the `inbox` (or use the web UI upload), and the background daemon will automatically parse the text, send it to a local Ollama instance, extract concepts, and organize them into decks of flashcards.
- **Leitner System Implementation**: Review flashcards using spaced repetition. Cards answered correctly move to higher boxes (with longer review intervals), and incorrectly answered cards return to Box 1.
- **Neon Cyberpunk Aesthetic**: Beautiful UI with 3D card flipping animations and glowing components.

## How to Run
1. Install dependencies: `pip install -r requirements.txt`
2. Run the background daemon to watch for files: `python3 daemon.py`
3. Run the web server: `uvicorn main:app --port 8080`

Navigate to `http://localhost:8080` to access the application.