# Data Alchemist

An autonomous, local AI-powered exploratory data analysis agent.

Data Alchemist continuously watches an `input/` folder for `.csv` and `.json` files.
Once a file is dropped in, it samples the dataset, sends the sample and metadata to a local Ollama instance (by default using `qwen2.5-coder:7b`), and asks it to generate a comprehensive Python script using `pandas`, `matplotlib`, and `seaborn` to perform Exploratory Data Analysis (EDA).

It then extracts the code, attempts to execute it, and if it fails, it feeds the stack trace back to Ollama to fix its own code—iterating up to 3 times in a self-healing loop.

Successful scripts will output summary insights to the console and save the generated visualizations directly into the `output/` directory.

## Setup

1. Make sure you have Ollama installed and running locally with the `qwen2.5-coder:7b` model:
   ```bash
   ollama pull qwen2.5-coder:7b
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Start the Data Alchemist:
   ```bash
   python alchemist.py
   ```

2. Drop a `.csv` or `.json` file into the `input/` directory.
3. Watch the magic happen in the console.
4. Check the `output/` directory for generated charts and visual insights.
