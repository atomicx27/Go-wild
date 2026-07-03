import requests
import json
import time

def check_ollama():
    try:
        response = requests.get('http://localhost:11434/api/tags')
        if response.status_code == 200:
            print("Ollama is running.")
            models = response.json().get('models', [])
            print(f"Available models: {[m['name'] for m in models]}")
            return True
        else:
            print(f"Failed to reach Ollama. Status: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"Connection error: {e}")
        return False

if __name__ == "__main__":
    check_ollama()
