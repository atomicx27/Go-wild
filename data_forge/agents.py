import urllib.request
import json

OLLAMA_API_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3"

def ask_ollama(prompt: str, json_format: bool = False, max_retries: int = 3) -> str:
    """Sends a prompt to the local Ollama instance and returns the response."""
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.2
        }
    }

    if json_format:
        payload["format"] = "json"

    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(OLLAMA_API_URL, data=data, headers={'Content-Type': 'application/json'})

    for attempt in range(max_retries):
        try:
            with urllib.request.urlopen(req, timeout=120) as response:
                result = json.loads(response.read().decode('utf-8'))
                return result.get('response', '')
        except Exception as e:
            if attempt == max_retries - 1:
                print(f"Error communicating with Ollama: {e}")
                return ""
            print(f"Ollama request failed (attempt {attempt+1}/{max_retries}), retrying...")
            import time
            time.sleep(2)
    return ""

class DataAnalyst:
    def analyze(self, csv_sample: str) -> dict:
        prompt = f"""You are an expert Data Analyst. Given the following CSV sample data, propose exactly 3 insightful visualizations that can be made using Chart.js.
Return ONLY valid JSON in the following format, with no markdown formatting, no code blocks, and no extra text.
{{
  "visualizations": [
    {{"title": "Chart Title", "type": "bar|line|pie|doughnut|etc", "description": "What this chart shows", "x_axis": "column_name", "y_axis": "column_name"}}
  ]
}}

CSV Sample Data:
{csv_sample}
"""
        response = ask_ollama(prompt, json_format=True)
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            print("DataAnalyst failed to return valid JSON. Returning raw response.")
            return {"error": "Invalid JSON", "raw_response": response}

class FrontendEngineer:
    def generate_dashboard(self, columns: list, analysis_plan: dict) -> str:
        prompt = f"""You are an expert Frontend Engineer. Your task is to generate a complete, single-file HTML dashboard using Tailwind CSS for styling, PapaParse for CSV parsing, and Chart.js for visualizations.

Analysis Plan from the Data Analyst:
{json.dumps(analysis_plan, indent=2)}

Columns available in the data: {', '.join(columns)}

CRITICAL REQUIREMENTS:
1. Include this EXACT placeholder script tag: <script id="csv-data" type="text/csv">__CSV_DATA__</script>
2. Parse the CSV data from that script tag using PapaParse.
3. Include CDN links for Tailwind CSS, PapaParse, and Chart.js.
4. Implement the 3 visualizations requested in the Analysis Plan using Chart.js.
5. Create a clean, modern, responsive layout using Tailwind CSS.
6. Handle any data transformation needed (e.g., parsing numbers, grouping).
7. ONLY output the raw HTML code. Do NOT wrap it in ```html or any markdown blocks. No explanations.

Generate the HTML now:
"""
        return ask_ollama(prompt)

class QAChecker:
    def verify(self, html_content: str) -> tuple[bool, str]:
        errors = []
        if "__CSV_DATA__" not in html_content:
            errors.append("Missing the __CSV_DATA__ placeholder.")
        if "Chart" not in html_content and "chart.js" not in html_content.lower():
            errors.append("Missing Chart.js library or usage.")
        if "Papa" not in html_content and "papaparse" not in html_content.lower():
            errors.append("Missing PapaParse library or usage.")
        if "tailwind" not in html_content.lower():
            errors.append("Missing Tailwind CSS.")

        if errors:
            return False, " ".join(errors)
        return True, "Passed"
