import os
import json
import urllib.request
import urllib.error
import glob
from pathlib import Path

# Common directories to ignore
IGNORE_DIRS = {'.git', 'node_modules', 'venv', 'env', '__pycache__', '.pytest_cache', 'build', 'dist', 'public', 'outbox', 'inbox', 'workspace'}
IGNORE_EXTS = {'.pyc', '.png', '.jpg', '.jpeg', '.gif', '.ico', '.pdf', '.zip', '.tar', '.gz', '.db', '.sqlite', '.sqlite3', '.json'}

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3"

def count_lines(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return sum(1 for _ in f)
    except Exception:
        return 0

def ask_ollama(file_content, filename):
    prompt = f"""
You are an expert software architect analyzing a codebase.
I will give you the contents of a file named '{filename}'.

Analyze this file and return ONLY a JSON object with the following schema:
{{
  "category": "UI" | "DATABASE" | "LOGIC" | "CONFIG" | "API" | "TEST" | "OTHER",
  "complexity": <integer from 1 to 10, where 1 is trivial and 10 is very complex>,
  "summary": "<A very concise 1-2 sentence description of what this file does>"
}}

File contents:
```
{file_content[:3000]} # Limit to 3000 chars to avoid context overflow for huge files
```
"""

    data = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
        "format": "json"
    }

    req = urllib.request.Request(OLLAMA_URL, data=json.dumps(data).encode('utf-8'), headers={'Content-Type': 'application/json'})

    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode('utf-8'))
            response_text = result.get('response', '{}')
            try:
                # Sometimes Ollama wraps it in markdown blocks even with format="json"
                response_text = response_text.replace('```json', '').replace('```', '').strip()
                return json.loads(response_text)
            except json.JSONDecodeError:
                return None
    except Exception as e:
        print(f"Error querying Ollama for {filename}: {e}")
        return None

def analyze_directory(target_dir):
    city_data = []

    target_path = Path(target_dir)
    if not target_path.exists() or not target_path.is_dir():
        print(f"Directory {target_dir} does not exist.")
        return city_data

    print(f"Metropolis Builder: Analyzing {target_dir}...")

    file_count = 0
    for root, dirs, files in os.walk(target_dir):
        # Mutate dirs in-place to ignore directories
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS and not d.startswith('.')]

        for file in files:
            if file.startswith('.') or any(file.endswith(ext) for ext in IGNORE_EXTS):
                continue

            filepath = os.path.join(root, file)
            rel_path = os.path.relpath(filepath, target_dir)
            lines = count_lines(filepath)

            if lines == 0:
                continue

            print(f"Analyzing: {rel_path} ({lines} lines)")
            file_count += 1

            # Read content
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
            except Exception:
                continue

            # Query Ollama
            ai_data = ask_ollama(content, file)

            # Fallback if Ollama fails or is not running
            if not ai_data:
                category = "OTHER"
                if file.endswith('.html') or file.endswith('.css') or file.endswith('.js'): category = "UI"
                elif 'db' in file or 'sql' in file: category = "DATABASE"
                elif file.endswith('.py'): category = "LOGIC"
                elif file.endswith('.md') or file.endswith('.yml'): category = "CONFIG"

                ai_data = {
                    "category": category,
                    "complexity": min(10, max(1, lines // 50)),
                    "summary": f"Could not reach Ollama. Default summary for {file}."
                }

            # Ensure required fields exist
            if 'category' not in ai_data: ai_data['category'] = "OTHER"
            if 'complexity' not in ai_data: ai_data['complexity'] = 1
            if 'summary' not in ai_data: ai_data['summary'] = "No summary provided."

            building_data = {
                "path": rel_path,
                "lines": lines,
                "category": ai_data['category'],
                "complexity": ai_data['complexity'],
                "summary": ai_data['summary']
            }
            city_data.append(building_data)

    print(f"Metropolis Builder: Finished analyzing {file_count} files.")
    return city_data

def build_city(target_dir, output_file):
    city_data = analyze_directory(target_dir)

    # Ensure public dir exists
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(city_data, f, indent=2)

    print(f"City data exported to {output_file}")
    return city_data

if __name__ == "__main__":
    # Test run on self
    build_city(os.path.dirname(os.path.dirname(__file__)), os.path.join(os.path.dirname(__file__), "public", "city_data.json"))