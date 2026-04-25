import requests
import json
import os

class OllamaClient:
    def __init__(self, host="http://localhost:11434", model="llama3"):
        self.host = host
        self.model = model
        self.api_url = f"{self.host}/api/chat"

    def chat(self, messages, temperature=0.7):
        """
        Sends a chat request to Ollama and returns the generated message.
        """
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature
            }
        }

        try:
            response = requests.post(self.api_url, json=payload)
            response.raise_for_status()
            data = response.json()
            return data.get("message", {}).get("content", "")
        except requests.exceptions.RequestException as e:
            return f"Error connecting to Ollama: {e}"

    def check_health(self):
        try:
            response = requests.get(f"{self.host}/api/tags")
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False
