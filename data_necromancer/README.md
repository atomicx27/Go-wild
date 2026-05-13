# Data Necromancer

An autonomous data analysis agent powered by Ollama. It resurrects dead datasets.

## How it works

Drop a `.csv` or `.json` file into the `inbox/` directory.

The `necromancer.py` agent continuously monitors the inbox. When it spots a dataset:
1. It moves the file into its `workspace/`.
2. It sends a small sample of the data to Ollama, asking for a Python script to analyze it (using `pandas`).
3. It runs the generated code. If the code crashes with a Python traceback, the agent feeds the error back to Ollama to fix the code (up to 3 retries).
4. Once the analysis succeeds, it prompts Ollama to write a second script (using `matplotlib`) to generate an insightful data visualization plot. It executes it using the same auto-correction loop.
5. Finally, it asks Ollama to write a comprehensive Markdown report summarizing the findings from the analysis output.
6. The entire resulting payload (original data file, generated analysis and visualization scripts, output plot `plot.png`, and the `report.md`) is packaged into a timestamped folder and delivered to the `outbox/`.

## Prerequisites

- [Ollama](https://ollama.ai/) running locally (`http://localhost:11434`).
- A robust code-generating model (default is `qwen2.5-coder:7b` but you can adjust `MODEL_NAME` in `necromancer.py`).

## Installation

```bash
pip install -r requirements.txt
```

## Running

```bash
python necromancer.py
```
Drop your datasets in the `inbox/` and watch the magic happen in the `outbox/`!