1. **Scaffold `cyber_deck` Subproject:**
   - Create the directory structure: `cyber_deck`, `cyber_deck/static`, `cyber_deck/static/css`, `cyber_deck/static/js`, `cyber_deck/tests`.
   - Write `cyber_deck/requirements.txt` including `fastapi`, `uvicorn`, `httpx`, and `pytest`.
   - Write `cyber_deck/README.md` explaining the Cyber Deck OS concept.

2. **Implement FastAPI Backend (`cyber_deck/main.py`):**
   - Serve static files from `cyber_deck/static` using absolute paths relative to `__file__`.
   - Implement `/api/chat` endpoint to proxy messages to Ollama (`/api/chat` endpoint) for general conversation.
   - Implement `/api/forge` endpoint that uses Ollama to generate single-file HTML/JS/CSS mini-apps based on user prompts.

3. **Implement Cyberpunk Frontend UI (`cyber_deck/static/index.html` & `cyber_deck/static/css/style.css`):**
   - Create a desktop environment layout with a taskbar, start menu, and desktop icons.
   - Apply modern UI/UX design: dark mode, neon accents, cyberpunk aesthetics, glassmorphism, and a CRT scanline overlay effect.
   - Include Tailwind CSS via CDN.

4. **Implement OS Logic & Built-in Apps (`cyber_deck/static/js/os.js`):**
   - Create a WindowManager class for draggable, closable, and focusable floating windows.
   - Implement "Terminal App": A chat interface communicating with `/api/chat`.
   - Implement "App Forge": An input interface that sends prompts to `/api/forge` and opens the resulting HTML payload in a new window containing an `iframe` with `srcdoc`.

5. **Implement Automated Tests (`cyber_deck/tests/test_main.py`):**
   - Write `pytest` tests using `fastapi.testclient.TestClient`.
   - Mock the Ollama HTTP calls to verify backend logic without requiring a live Ollama instance.
   - Run the tests to ensure passing state.

6. **Repository Integration:**
   - Append `cyber_deck` to the root `.gitignore` (e.g., `cyber_deck/venv/`, `cyber_deck/__pycache__/`).
   - Append a description of `cyber_deck` to the root `README.md`.

7. **Pre-commit Steps:**
   - Complete pre-commit steps to ensure proper testing, verification, review, and reflection are done.

8. **Submit:**
   - Submit the changes with a descriptive commit message.
