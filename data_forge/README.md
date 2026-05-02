# Data Forge

Data Forge is an autonomous, multi-agent AI pipeline that instantly turns raw CSV files into beautiful, single-page interactive HTML dashboards.

## How it works

It uses a localized AI (via Ollama) and a team of specialized agent prompts:
1. **Data Analyst**: Reads a sample of the CSV and formulates a JSON plan for visualizations.
2. **Frontend Engineer**: Takes the raw column headers and the analyst's plan to write an entire HTML document. The document uses Tailwind CSS for layout, PapaParse for parsing, and Chart.js for visualizations.
3. **QA Checker**: Validates that the generated HTML has all the required libraries and the exact placeholder for the CSV data. If it fails, the Engineer re-attempts the generation up to 3 times.

## Usage

1. Ensure Ollama is running locally (`http://localhost:11434`) and has the `llama3` model pulled (`ollama run llama3`).
2. Run the main orchestration loop:
   ```bash
   python main.py
   ```
3. Drop any `.csv` file into the `data_forge/inbox/` directory.
4. The system will automatically detect it, spin up the agents, and eventually output a single `.html` file in `data_forge/outbox/` containing an interactive dashboard with the embedded CSV data. The original CSV is moved to `data_forge/processed/`.

## Architecture
- Pure Python (no dependencies required).
- Completely local and autonomous.
