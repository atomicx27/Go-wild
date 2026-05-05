import urllib.request
import urllib.error
import json

def chat(prompt, model="llama3", url="http://localhost:11434/api/generate"):
    """
    Sends a prompt to the Ollama API and returns the response.
    Includes a fallback mechanism if the server is unreachable.
    """
    data = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }

    req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), method='POST')
    req.add_header('Content-Type', 'application/json')

    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode('utf-8'))
            return result.get("response", "")
    except (urllib.error.URLError, ConnectionError) as e:
        print(f"[Ollama Client Warning] Could not connect to Ollama server at {url}. Error: {e}")
        print("Falling back to mock response.")
        return _mock_chat_response(prompt)
    except Exception as e:
        print(f"[Ollama Client Error] An unexpected error occurred: {e}")
        return ""

def _mock_chat_response(prompt):
    """
    Provides mock responses for testing when Ollama is unavailable.
    """
    prompt_lower = prompt.lower()

    if "python" in prompt_lower and ("script" in prompt_lower or "code" in prompt_lower):
        # Provide a basic Python script structure
        return """
```python
import sys

def main():
    print("Mock tool executed with arguments:", sys.argv[1:])

if __name__ == "__main__":
    main()
```
"""
    elif "json" in prompt_lower or "plan" in prompt_lower or "registry" in prompt_lower:
        # Provide a JSON structure if requested
        return """
```json
{
    "action": "create_new",
    "tool_name": "mock_tool",
    "reasoning": "Mock reasoning."
}
```
"""
    elif "exact bash command" in prompt_lower or "command" in prompt_lower:
        # Provide a mock execution command
        return "python3 the_toolmaker/tools/mock_tool.py mock_args"
    else:
        return "This is a mock response from the Toolmaker's Ollama fallback client. The server was unreachable."

if __name__ == "__main__":
    print("Testing Ollama Client...")
    print(chat("Hello, are you there?"))
