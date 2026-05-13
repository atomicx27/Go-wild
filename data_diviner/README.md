# Data Diviner

An autonomous Data Analyst Agent powered by a local Ollama instance.

Data Diviner takes any CSV file, automatically loads it into an in-memory SQLite database, and accepts plain English questions about the data. Using a ReAct (Reasoning and Acting) loop, the agent writes its own SQL queries, executes them against the database, observes the results, and iterately works towards a final answer.

## Features
- **Zero External Dependencies**: Pure Python using standard libraries (`sqlite3`, `csv`, `urllib.request`).
- **Autonomous Reasoning**: Doesn't just generate SQL; it executes it, checks for errors, views the results, and decides what to do next.
- **Local AI**: Fully private and offline via Ollama.

## Usage

Ensure Ollama is running locally (e.g., `ollama serve` and `ollama run llama3`).

```bash
# Basic query
python diviner.py sample_data.csv "What is the total sales amount for Electronics?"

# See the agent's thought process
python diviner.py sample_data.csv "Which region had the most laptop sales?" --verbose

# Use a different model
python diviner.py sample_data.csv "How many unique categories are there?" --model mistral
```
