# Autonomous Coder Swarm

An agentic background worker that automatically generates Python code from natural language prompts using Ollama locally.

## Setup

1. Install dependencies:
   ```bash
   pip install requests rich
   ```
2. Start your local Ollama server and pull `qwen2.5-coder:0.5b`:
   ```bash
   ollama pull qwen2.5-coder:0.5b
   ollama serve
   ```

## Usage

1. Run the agent in the background:
   ```bash
   python3 run_agent.py
   ```
2. Drop `.txt` files containing your natural language prompts into the `inbox/` directory.
   ```bash
   echo "Write a python script that prints the first 10 fibonacci numbers" > inbox/my_prompt.txt
   ```
3. The agent will automatically read it, generate the python code via Ollama, and save the result into the `scripts/` directory as `my_prompt_output.py`.
4. The original prompt is then moved to the `processed/` directory. If any errors occur, it is moved to `rejected/`.

## Tests

To run the automated tests, use `pytest`:
```bash
pip install pytest responses
PYTHONPATH=. pytest test_agent.py
```
