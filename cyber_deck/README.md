# Cyber Deck OS

An experimental, web-based "operating system" UI built with FastAPI and a Cyberpunk/Neon aesthetic.
It includes a full window manager and integrates with Ollama to provide:
1.  **Terminal App**: An AI chat interface right on your desktop.
2.  **App Forge**: An agentic mini-app generator. You prompt it, and it writes HTML/JS/CSS, launching the result in a new floating window.

## Running

```bash
cd cyber_deck
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

Then visit `http://localhost:8000`
