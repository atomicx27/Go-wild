import json
import urllib.request
import urllib.error

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3"

def call_ollama(prompt, system_prompt=""):
    """
    Calls the local Ollama instance. If it fails, returns a mock response.
    """
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "system": system_prompt,
        "stream": False
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(OLLAMA_URL, data=data, headers={'Content-Type': 'application/json'})

    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            result = json.loads(response.read().decode("utf-8"))
            return result.get("response", "")
    except (urllib.error.URLError, ConnectionError, Exception) as e:
        # Graceful fallback if Ollama isn't running or fails
        return f"[Mock Response] I'm just a simple dev pet. (Ollama connection failed: {e})"
