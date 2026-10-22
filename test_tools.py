import requests
import json

payload = {
    "model": "llama3.2",
    "messages": [{"role": "user", "content": "Run the 'uptime' command."}],
    "stream": False,
    "tools": [
        {
            "type": "function",
            "function": {
                "name": "run_command",
                "description": "Executes a shell command.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "command": {"type": "string", "description": "The bash command"}
                    },
                    "required": ["command"]
                }
            }
        }
    ]
}

response = requests.post("http://localhost:11434/api/chat", json=payload)
print(response.status_code)
print(json.dumps(response.json(), indent=2))
