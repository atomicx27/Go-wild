import requests
import json
import re

class OllamaAgent:
    def __init__(self, model="qwen2.5-coder:0.5b", base_url="http://localhost:11434"):
        self.model = model
        self.base_url = base_url
        self.api_url = f"{self.base_url}/api/generate"

    def generate(self, prompt, system_prompt=None):
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False
        }
        if system_prompt:
            payload["system"] = system_prompt

        try:
            response = requests.post(self.api_url, json=payload)
            response.raise_for_status()
            return response.json().get("response", "")
        except requests.exceptions.RequestException as e:
            return f"Error connecting to Ollama: {e}"

    def extract_code(self, text):
        # Extract python code from markdown blocks
        pattern = r"```python\n(.*?)\n```"
        match = re.search(pattern, text, re.DOTALL)
        if match:
            return match.group(1)

        # Try generic code block
        pattern_generic = r"```\n(.*?)\n```"
        match_generic = re.search(pattern_generic, text, re.DOTALL)
        if match_generic:
            return match_generic.group(1)

        return text.strip() # return text if no block found

    def execute_and_heal(self, prompt, max_retries=3):
        system_prompt = "You are an autonomous Python developer. You will be given a task. Return ONLY valid python code enclosed in ```python...``` blocks. Do NOT include explanations outside the code blocks."

        current_prompt = f"Write python code for the following task: {prompt}"

        for attempt in range(max_retries):
            # Generate code
            response_text = self.generate(current_prompt, system_prompt=system_prompt)
            code = self.extract_code(response_text)

            # Write to temporary file
            with open("temp_script.py", "w") as f:
                f.write(code)

            # Execute
            import subprocess
            try:
                result = subprocess.run(["python3", "temp_script.py"], capture_output=True, text=True, timeout=10)

                if result.returncode == 0:
                    return {
                        "success": True,
                        "code": code,
                        "output": result.stdout,
                        "attempts": attempt + 1
                    }
                else:
                    error_msg = result.stderr or result.stdout
                    current_prompt = f"The previous code failed with the following error:\n\n{error_msg}\n\nPlease provide fixed Python code for the original task: {prompt}"

            except subprocess.TimeoutExpired:
                current_prompt = f"The previous code timed out. Please provide more efficient Python code for the original task: {prompt}"
            except Exception as e:
                current_prompt = f"An unexpected error occurred during execution: {e}. Please provide fixed Python code for the original task: {prompt}"

        return {
            "success": False,
            "code": code,
            "output": "Max retries reached without success.",
            "attempts": max_retries
        }
