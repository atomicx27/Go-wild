import json
import logging
import os
import requests
import subprocess
import traceback

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DataDetective:
    def __init__(self, ollama_url="http://localhost:11434", model="llama3", output_dir="output"):
        self.ollama_url = ollama_url
        self.model = model
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def _call_ollama(self, prompt, system_prompt="You are an expert data scientist and Python developer."):
        """Calls the local Ollama instance with a prompt."""
        url = f"{self.ollama_url}/api/generate"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "system": system_prompt,
            "stream": False
        }
        try:
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()
            data = response.json()
            return data.get("response", "").strip()
        except requests.exceptions.RequestException as e:
            logger.warning(f"Failed to connect to Ollama: {e}")
            return self._mock_response(prompt)

    def _mock_response(self, prompt):
        """Provides a mock response when Ollama is unavailable."""
        logger.info("Using mock response due to Ollama unavailability.")
        if "analyze the following dataset" in prompt.lower() or "python script" in prompt.lower():
            # Return a generic mock script
            return f"""```python
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

print("Mock Analysis Insights:")
print("- Revenue is trending upwards.")
print("- Widgets are the top-selling category.")

# Create a mock plot
plt.figure(figsize=(8, 6))
plt.plot([1, 2, 3], [10, 20, 30])
plt.title("Mock Sales Trend")
plt.xlabel("Time")
plt.ylabel("Sales")
os.makedirs('{self.output_dir}', exist_ok=True)
plt.savefig('{self.output_dir}/sales_trend.png')
print("Generated plot at {self.output_dir}/sales_trend.png")
```"""
        elif "report" in prompt.lower():
            return f"# Data Detective Final Report\n\n## Insights\n- Revenue is trending upwards.\n- Widgets are the top-selling category.\n\n## Visualizations\n![Sales Trend]({self.output_dir}/sales_trend.png)\n"
        else:
            return "Mock fallback response."

    def _extract_python_code(self, response):
        """Extracts python code from markdown block if present."""
        if "```python" in response:
            parts = response.split("```python")
            if len(parts) > 1:
                return parts[1].split("```")[0].strip()
        elif "```" in response:
             parts = response.split("```")
             if len(parts) > 1:
                 return parts[1].strip()
        return response.strip()

    def analyze(self, csv_filepath):
        """Analyzes the given CSV file using a generated python script."""
        logger.info(f"Starting analysis of {csv_filepath}")

        try:
            import pandas as pd
            df = pd.read_csv(csv_filepath)
            sample_data = df.head(5).to_csv(index=False)
            columns = ", ".join(df.columns)
        except Exception as e:
            logger.error(f"Failed to read CSV: {e}")
            return False

        prompt = f"""
I have a dataset with the following columns: {columns}
Here is a sample of the first 5 rows:
{sample_data}

Write a complete, self-contained Python script to analyze this data.
The script MUST:
1. Load the data from '{csv_filepath}' using pandas.
2. Perform some meaningful analysis (e.g., aggregations, trends).
3. Print out at least 3 bullet points of insights to stdout.
4. Generate at least one chart (using matplotlib or seaborn) and save it to the '{self.output_dir}' directory as a PNG file.
5. Make sure the output directory exists using os.makedirs.

Return ONLY the python code inside a ```python ``` markdown block.
"""
        max_retries = 3
        script_path = "generated_script.py"

        for attempt in range(max_retries):
            logger.info(f"Generating script (Attempt {attempt + 1}/{max_retries})")
            response = self._call_ollama(prompt)
            code = self._extract_python_code(response)

            with open(script_path, "w") as f:
                f.write(code)

            logger.info(f"Executing generated script...")
            try:
                result = subprocess.run(
                    ["python3", script_path],
                    capture_output=True,
                    text=True,
                    check=True
                )
                logger.info("Script executed successfully.")
                return result.stdout
            except subprocess.CalledProcessError as e:
                logger.error(f"Script execution failed:\n{e.stderr}")
                if attempt < max_retries - 1:
                    logger.info("Attempting to fix script...")
                    prompt = f"""
The previous python script you generated failed with this error:
{e.stderr}

Here is the code that failed:
```python
{code}
```

Please fix the error and provide the corrected python code.
Return ONLY the python code inside a ```python ``` markdown block.
"""
                else:
                    logger.error("Max retries reached. Analysis failed.")
                    return False
        return False

    def generate_report(self, insights, report_path="report.md"):
        """Compiles a final report using the generated insights and images."""
        logger.info("Generating final report...")

        images = []
        if os.path.exists(self.output_dir):
            images = [f for f in os.listdir(self.output_dir) if f.endswith(".png")]

        image_list_str = "\n".join([f"- {img}" for img in images])

        prompt = f"""
I have run an automated data analysis. Here are the printed insights from the script:
{insights}

The script also generated the following visualization files in the '{self.output_dir}' directory:
{image_list_str}

Please compile a professional Markdown report summarizing these findings.
Include the insights clearly, and embed the visualizations using Markdown image syntax (e.g. `![Description]({self.output_dir}/filename.png)`).
Return ONLY the Markdown content.
"""
        report_content = self._call_ollama(prompt, system_prompt="You are a professional data analyst compiling reports.")

        # Clean up possible markdown wrappers
        if report_content.startswith("```markdown"):
            report_content = report_content[len("```markdown"):].strip()
        if report_content.endswith("```"):
            report_content = report_content[:-3].strip()

        with open(report_path, "w") as f:
            f.write(report_content)

        logger.info(f"Report saved to {report_path}")
        return report_path

if __name__ == "__main__":
    detective = DataDetective(output_dir="output")
    csv_file = "sample_data.csv"

    insights = detective.analyze(csv_file)
    if insights:
        detective.generate_report(insights)
    else:
        logger.error("Failed to generate insights, skipping report.")
