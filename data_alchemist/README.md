# Data Alchemist

Data Alchemist is an autonomous agent that processes data files (CSVs, JSONs, etc.) dropped into an inbox. It uses a local Ollama instance to generate Python code to analyze the data, self-heals if the code fails, extracts text insights and visualizations, and finally packages everything into a beautiful HTML dashboard in an outbox.

## Features

- **Autonomous Data Analysis**: Just drop a file in the inbox.
- **LLM Code Generation**: Asks Ollama (`llama3`) to write python analysis scripts (pandas, matplotlib, seaborn).
- **Self-Healing Execution**: If the generated python script crashes, Data Alchemist feeds the traceback back to Ollama to fix the code automatically.
- **Dashboard Generation**: Compiles the final insights and generated plots into a modern HTML file.

## Prerequisites

- Python 3
- A running local instance of [Ollama](https://ollama.com/) (defaults to `http://localhost:11434`).
- Ensure `llama3` is pulled: `ollama run llama3`

The generated code might require data science libraries. You can install standard ones to your environment:
```bash
pip install pandas matplotlib seaborn scikit-learn
```

## How to Use

1. Start the Data Alchemist daemon:
   ```bash
   python alchemist.py
   ```
2. Drop a dataset (e.g., `sales_data.csv`) into the `data_alchemist/inbox/` directory.
3. Watch the terminal as the alchemist reads the sample, generates code, executes it, self-heals, and generates the dashboard.
4. Open the `dashboard.html` located in the newly created folder inside `data_alchemist/outbox/` to view the final results.
