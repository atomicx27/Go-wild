import json
import urllib.request
import urllib.error

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "qwen2.5-coder:7b" # Standard decent local coder model, can be overridden

def generate_completion(prompt, model=MODEL_NAME, system=""):
    """Generates a standard completion from Ollama."""
    data = {
        "model": model,
        "prompt": prompt,
        "system": system,
        "stream": False
    }

    req = urllib.request.Request(
        OLLAMA_URL,
        data=json.dumps(data).encode('utf-8'),
        headers={'Content-Type': 'application/json'}
    )

    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            return result.get('response', '')
    except urllib.error.URLError as e:
        print(f"Failed to connect to Ollama: {e}")
        return f"Error: Could not connect to Ollama. Make sure it's running locally at http://localhost:11434."

def generate_stream(prompt, model=MODEL_NAME, system=""):
    """Generates a streaming completion from Ollama, yielding chunks."""
    data = {
        "model": model,
        "prompt": prompt,
        "system": system,
        "stream": True
    }

    req = urllib.request.Request(
        OLLAMA_URL,
        data=json.dumps(data).encode('utf-8'),
        headers={'Content-Type': 'application/json'}
    )

    try:
        with urllib.request.urlopen(req) as response:
            for line in response:
                if line:
                    chunk = json.loads(line.decode('utf-8'))
                    if 'response' in chunk:
                        yield chunk['response']
    except urllib.error.URLError as e:
        print(f"Failed to connect to Ollama for streaming: {e}")
        yield f"Error: Could not connect to Ollama."

if __name__ == "__main__":
    # Test connection
    print("Testing standard completion...")
    print(generate_completion("Say hello world in python."))
