import json
import urllib.request
import urllib.error
import re
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

OLLAMA_URL = "http://localhost:11434/api/chat"
DEFAULT_MODEL = "llama3"

def chat_with_ollama(messages, model=DEFAULT_MODEL, temperature=0.7):
    """
    Sends a chat request to the local Ollama instance.
    Uses the /api/chat endpoint.
    """
    payload = {
        "model": model,
        "messages": messages,
        "stream": False,
        "options": {
            "temperature": temperature
        }
    }

    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(OLLAMA_URL, data=data, headers={'Content-Type': 'application/json'})

    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            return result.get("message", {}).get("content", "")
    except urllib.error.URLError as e:
        logger.error(f"Failed to connect to Ollama: {e}")
        return f"Error: Unable to reach Ollama at {OLLAMA_URL}."
    except Exception as e:
        logger.error(f"Ollama API error: {e}")
        return f"Error: {e}"

def extract_code_blocks(text, language="python"):
    """
    Extracts code blocks from markdown text for a specific language.
    Falls back to generic code blocks if specific language is not found.
    """
    # Try to find specific language block first
    pattern = rf"```{language}\n(.*?)```"
    matches = re.findall(pattern, text, re.DOTALL | re.IGNORECASE)

    if matches:
        return "\n\n".join(matches)

    # Fallback to generic code blocks
    pattern = r"```(?:\w+)?\n(.*?)```"
    matches = re.findall(pattern, text, re.DOTALL)

    if matches:
        return "\n\n".join(matches)

    # If no markdown code blocks, try to heuristically check if it's pure code
    if "import " in text or "def " in text or "class " in text:
        return text.strip()

    return ""
