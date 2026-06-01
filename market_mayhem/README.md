# Market Mayhem: Cyberpunk Terminal

An autonomous, multi-agent stock market simulation powered by a local Ollama instance. Watch as distinct AI personas (The Ape, The Suit, The Chaos Bot) trade synthetic stocks in real-time, reacting to randomly generated breaking news headlines, all visualized in a cyberpunk-themed Terminal UI.

## Features
- **Local AI Powered**: Uses Ollama (defaulting to `llama3`) to drive the decision-making of the AI traders and a chaotic news anchor.
- **Distinct Personas**: Each trader has a specific system prompt defining their behavior, leading to different trading strategies (or lack thereof).
- **Simulated Market**: A simple random-walk stock engine with sentiment drift driven by the AI news anchor's headlines.
- **Cyberpunk TUI**: A beautiful, real-time Terminal User Interface built with `rich`.

## Requirements
- Python 3.10+
- `rich`
- `requests`
- A running local instance of [Ollama](https://ollama.com/) with the `llama3` model pulled (`ollama run llama3`).

## Setup and Running

1. **Create and activate a virtual environment (optional but recommended):**
   ```bash
   cd market_mayhem
   python3 -m venv venv
   source venv/bin/activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Ensure Ollama is running:**
   Make sure you have Ollama running locally at `http://localhost:11434`.

4. **Run the simulation:**
   ```bash
   python3 main.py
   ```

5. **Stop the simulation:**
   Press `Ctrl+C` to terminate the program.
