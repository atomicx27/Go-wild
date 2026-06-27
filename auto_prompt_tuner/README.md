# Auto Prompt Tuner

Auto Prompt Tuner is an agentic tool that automatically optimizes prompts for LLMs using an evolutionary algorithm approach.
It takes a base prompt, an evaluation criterion (or test cases), and iteratively mutates, evaluates, and selects the best performing prompt using a local Ollama model (e.g., `qwen2.5:0.5b` or `llama3`).

## Features
- Iterative prompt refinement based on automated feedback.
- Generates multiple prompt variations (mutations).
- Evaluates prompts against a defined target/ground truth.
- Completely autonomous workflow.

## Prerequisites
- Python 3
- A running local instance of [Ollama](https://ollama.com/) (defaults to `http://localhost:11434`).
- Ensure the model you want to use is pulled (e.g., `ollama pull qwen2.5:0.5b`)

Install the required python packages:
```bash
pip install -r requirements.txt
```

## Usage
1. Make sure Ollama is running (`ollama serve &`) and the model is pulled.
2. Run `python tuner.py` to start the optimization process.
