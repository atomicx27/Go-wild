import os
import json
import requests
import argparse
import shutil
from pathlib import Path

OLLAMA_URL = "http://localhost:11434/api/chat"

def get_python_files(directory):
    return list(Path(directory).rglob("*.py"))

def analyze_codebase(files_content):
    prompt = """
    You are an expert software architect. Analyze the following Python codebase.
    Provide two things in JSON format:
    1. A detailed, cyberpunk-themed 'summary' of the project's capabilities.
    2. A 'mermaid' string containing a valid Mermaid.js graph diagram illustrating the architecture. Do not include markdown codeblocks for the mermaid string, just the raw mermaid syntax.

    Respond ONLY with valid JSON in the format:
    {
      "summary": "...",
      "mermaid": "graph TD\\n..."
    }
    """

    messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": f"Codebase:\n\n{files_content}"}
    ]

    try:
        response = requests.post(OLLAMA_URL, json={
            "model": "llama3",
            "messages": messages,
            "format": "json",
            "stream": False
        })
        response.raise_for_status()
        data = response.json()
        content = data.get("message", {}).get("content", "")
        return json.loads(content)
    except Exception as e:
        print(f"Error calling Ollama: {e}")
        return {"summary": "Failed to generate summary.", "mermaid": "graph TD\n  A[Error] --> B[Failed to generate]"}

def run_agent(target_dir):
    py_files = get_python_files(target_dir)

    if not py_files:
        print("No Python files found.")
        return

    code_content = ""
    for pf in py_files:
        try:
            with open(pf, 'r', encoding='utf-8') as f:
                code_content += f"\n--- {pf} ---\n{f.read()}\n"
        except Exception as e:
            print(f"Failed to read {pf}: {e}")

    print(f"Analyzing {len(py_files)} files...")
    analysis = analyze_codebase(code_content[:10000]) # Truncate to avoid huge context issues

    summary = analysis.get("summary", "No summary.")
    mermaid_code = analysis.get("mermaid", "graph TD\n  A[Error]")

    base_dir = Path(__file__).parent
    template_path = base_dir / "template.html"

    if not template_path.exists():
        print(f"Template not found at {template_path}")
        return

    with open(template_path, 'r', encoding='utf-8') as f:
        html = f.read()

    html = html.replace("{{ SUMMARY }}", summary)
    html = html.replace("{{ MERMAID }}", mermaid_code)

    output_dir = base_dir / "output_docs"
    output_dir.mkdir(exist_ok=True)
    output_file = output_dir / "index.html"

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)

    # Copy the CSS file so the output docs have the styling
    css_source = base_dir / "style.css"
    if css_source.exists():
        shutil.copy(css_source, output_dir / "style.css")

    print(f"Documentation generated at {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Synth Scribe - Documentation Agent")
    parser.add_argument("target_dir", type=str, help="Target directory to analyze")
    args = parser.parse_args()

    run_agent(args.target_dir)
