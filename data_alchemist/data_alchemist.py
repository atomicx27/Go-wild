import pandas as pd
import matplotlib.pyplot as plt
import requests
import json
import os
import random
import csv
from typing import Dict, Any

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3"

def generate_sample_data(filepath: str = "sample_data.csv") -> str:
    """Generates a sample e-commerce dataset if one doesn't exist."""
    if not os.path.exists(filepath):
        print(f"Generating sample dataset at {filepath}...")
        with open(filepath, 'w', newline='') as csvfile:
            fieldnames = ['order_id', 'product_category', 'price', 'quantity', 'date', 'customer_age']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            categories = ['Electronics', 'Clothing', 'Home & Garden', 'Toys', 'Sports']
            for i in range(100):
                writer.writerow({
                    'order_id': i + 1,
                    'product_category': random.choice(categories),
                    'price': round(random.uniform(10.0, 500.0), 2),
                    'quantity': random.randint(1, 5),
                    'date': f"2023-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}",
                    'customer_age': random.randint(18, 70)
                })
    return filepath

def query_ollama(prompt: str, system_prompt: str = "") -> str:
    """Queries the Ollama API with a fallback mechanism."""
    payload = {
        "model": MODEL,
        "prompt": prompt,
        "system": system_prompt,
        "stream": False
    }
    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=10)
        response.raise_for_status()
        return response.json().get("response", "")
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
        print(f"Ollama connection error: {e}. Using mock response.")
        return get_mock_response(prompt)
    except Exception as e:
         print(f"Unexpected error: {e}")
         return get_mock_response(prompt)

def get_mock_response(prompt: str) -> str:
    """Provides mock responses for testing without Ollama."""
    prompt_lower = prompt.lower()
    if "question" in prompt_lower or "propose" in prompt_lower:
        return "1. What is the total revenue by product category?\n2. How does customer age correlate with the quantity of items purchased?\n3. What is the monthly trend of sales?"
    elif "code" in prompt_lower or "python" in prompt_lower:
        return """
```python
import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('sample_data.csv')
revenue = df.groupby('product_category')['price'].sum()

plt.figure(figsize=(10, 6))
revenue.plot(kind='bar')
plt.title('Total Revenue by Product Category')
plt.xlabel('Product Category')
plt.ylabel('Total Revenue ($)')
plt.tight_layout()
plt.savefig('plot_1.png')
plt.close()
print("Plot saved as plot_1.png")
```
"""
    elif "report" in prompt_lower or "summarize" in prompt_lower:
        return "# Data Alchemist Report\n\n## Findings\n\nBased on the analysis, we observed significant trends in revenue across different product categories. The generated plots provide visual evidence of these patterns.\n\n- The highest revenue category was identified.\n- Customer age shows interesting purchasing behaviors.\n- Monthly sales exhibit seasonal variations."
    return "This is a mock response from Data Alchemist."

def get_schema(df: pd.DataFrame) -> str:
    """Extracts schema information from a DataFrame."""
    schema = []
    for col in df.columns:
        dtype = str(df[col].dtype)
        sample_vals = df[col].dropna().head(3).tolist()
        schema.append(f"- Column '{col}' (Type: {dtype}), Sample values: {sample_vals}")
    return "\n".join(schema)

def extract_python_code(text: str) -> str:
    """Extracts python code blocks from markdown text."""
    if "```python" in text:
        return text.split("```python")[1].split("```")[0].strip()
    elif "```" in text:
        return text.split("```")[1].split("```")[0].strip()
    return text.strip()

def run_agentic_loop(df: pd.DataFrame, schema_info: str) -> Dict[str, Any]:
    """Runs the Ollama ReAct loop to generate analysis questions and code."""
    results = {}

    # Step 1: Generate a question
    print("\n--- Step 1: Generating Analysis Questions ---")
    question_prompt = f"Given the following dataset schema:\n{schema_info}\n\nPropose exactly ONE interesting analytical question that can be answered using this data. Output only the question."
    question = query_ollama(question_prompt, "You are an expert data analyst. Be concise.")
    print(f"Proposed Question: {question}")

    # Step 2: Generate Code
    print("\n--- Step 2: Generating Python Code ---")
    code_prompt = f"""Given the dataset schema:
{schema_info}
The data is available in a file named 'sample_data.csv'.
Write a python script using pandas and matplotlib to answer this question: {question}
The script must:
1. Load 'sample_data.csv'
2. Perform the analysis
3. Save the resulting plot as 'plot_1.png'
4. Print the key findings.
Output ONLY the python code inside ```python ``` blocks, without any explanation.
"""
    raw_code_response = query_ollama(code_prompt, "You are an expert python programmer. Output only code.")
    code = extract_python_code(raw_code_response)
    print(f"Generated Code:\n{code}")

    # Step 3: Execute Code (with a retry loop)
    print("\n--- Step 3: Executing Code ---")
    max_retries = 2
    success = False

    # To keep it simple and autonomous, we execute using exec.
    # Warning: In a real world scenario, executing arbitrary code from an LLM is dangerous.
    for attempt in range(max_retries):
        try:
            print(f"Execution attempt {attempt + 1}...")
            # Capture standard output
            import io
            from contextlib import redirect_stdout
            f = io.StringIO()
            with redirect_stdout(f):
                exec(code, globals())
            output = f.getvalue()
            print(f"Execution Output:\n{output}")
            success = True
            results['question'] = question
            results['code'] = code
            results['output'] = output
            results['plot_file'] = 'plot_1.png'
            break
        except Exception as e:
            error_msg = str(e)
            print(f"Execution failed: {error_msg}")
            if attempt < max_retries - 1:
                print("Asking Ollama to fix the code...")
                fix_prompt = f"The following python code:\n```python\n{code}\n```\nFailed with this error:\n{error_msg}\n\nPlease fix the code and output the corrected version inside ```python ``` blocks."
                raw_code_response = query_ollama(fix_prompt, "You are a python debugging expert. Output only code.")
                code = extract_python_code(raw_code_response)
            else:
                print("Max retries reached. Analysis failed.")
                results['error'] = error_msg

    return results

def generate_report(results: Dict[str, Any]):
    """Uses Ollama to summarize the findings into a markdown report."""
    print("\n--- Step 4: Compiling Final Report ---")
    if 'error' in results:
        print("Analysis failed, generating error report.")
        report_content = f"# Data Alchemist Analysis Failed\n\n**Error:**\n```\n{results['error']}\n```"
    else:
        summary_prompt = f"""Based on the following analysis:
Question: {results['question']}
Code Output: {results['output']}

Write a brief markdown summary of the findings. Do not include the python code.
"""
        report_text = query_ollama(summary_prompt, "You are a data reporting assistant.")
        report_content = f"{report_text}\n\n## Visualization\n\n![Analysis Plot]({results.get('plot_file', '')})"

    with open('report.md', 'w') as f:
        f.write(report_content)
    print("Report saved to report.md")

def main():
    print("Data Alchemist initializing...")
    data_file = generate_sample_data()

    try:
        df = pd.read_csv(data_file)
        print(f"Successfully loaded dataset with {len(df)} rows.")
        schema_info = get_schema(df)
        print("\nDataset Schema:")
        print(schema_info)

        results = run_agentic_loop(df, schema_info)
        generate_report(results)

    except Exception as e:
        print(f"Error during execution: {e}")

if __name__ == "__main__":
    main()
