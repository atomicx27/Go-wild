# Gossip Protocol

An autonomous AI agent simulation where agents gossip with each other, extract new information, and update their memories dynamically using a local Ollama instance (`llama3.2:1b`).

## Setup

1. Install Ollama and pull the required model:
   ```bash
   ollama pull llama3.2:1b
   ```
2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Simulation

1. Start the API server:
   ```bash
   uvicorn api:app --port 8000
   ```
2. Start the autonomous agent simulation loop:
   ```bash
   python simulation.py
   ```
3. Open your browser and navigate to `http://localhost:8000` to view the live Gossip Protocol Dashboard.
