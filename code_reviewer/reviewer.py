import os
import sys
import json
import urllib.request
import urllib.error

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434/api/generate")
MODEL = os.environ.get("OLLAMA_MODEL", "qwen2.5:0.5b")

def query_ollama(prompt):
    data = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False
    }

    req = urllib.request.Request(OLLAMA_URL, data=json.dumps(data).encode('utf-8'), headers={'Content-Type': 'application/json'})

    try:
        response = urllib.request.urlopen(req)
        result = json.loads(response.read().decode('utf-8'))
        return result.get("response", "")
    except Exception as e:
        print(f"Error querying Ollama: {e}")
        return None

def review_file(filepath):
    if not os.path.exists(filepath):
        print(f"Error: File '{filepath}' not found.")
        return

    with open(filepath, 'r', encoding='utf-8') as f:
        code = f.read()

    print(f"Reviewing {filepath}...")

    prompt = f"""You are an expert Python code reviewer.
Please review the following code. Focus on:
1. Potential bugs or edge cases.
2. Code readability and adherence to PEP 8 standards.
3. Performance improvements.
4. Security concerns (if any).

Code:
```python
{code}
```

Provide a concise, constructive review.
"""

    review = query_ollama(prompt)
    if review:
        print("\n--- Review Output ---\n")
        print(review)
        print("\n---------------------\n")
    else:
        print("Failed to get review.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python reviewer.py <file_to_review.py>")
        sys.exit(1)

    review_file(sys.argv[1])
