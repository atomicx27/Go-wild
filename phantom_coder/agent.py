import requests
import json
import re

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3"

def generate_code(prompt: str, language: str) -> str:
    """Calls Ollama to generate code based on the prompt."""

    system_prompt = f"""You are Phantom Coder, an expert {language} developer.
You have been summoned to write a specific piece of code.
The user will provide a comment or a brief description of what they want.
Your ONLY output must be the raw {language} code that implements the request.
DO NOT include markdown code blocks (like ```python).
DO NOT include any explanation, intro, or outro text.
ONLY output the code."""

    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL_NAME,
                "prompt": prompt,
                "system": system_prompt,
                "stream": False,
            },
            timeout=30,
        )
        response.raise_for_status()
        result = response.json().get("response", "").strip()

        # Fallback: remove markdown block formatting if the model still includes it
        if result.startswith("```"):
            # find the first newline to skip the ```python part
            first_newline = result.find("\n")
            if first_newline != -1:
                result = result[first_newline+1:]

            if result.endswith("```"):
                result = result[:-3]

        return result.strip()
    except Exception as e:
        print(f"Error calling Ollama: {e}")
        return f"// Error: Could not generate code due to {e}"
