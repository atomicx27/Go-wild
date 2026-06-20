import os
import time
import requests
import json
import re
from rich.console import Console

console = Console()

class AutonomousCoderSwarm:
    def __init__(self, base_dir="autonomous_coder_swarm", model="qwen2.5-coder:0.5b", ollama_url="http://localhost:11434/api/generate"):
        self.base_dir = base_dir
        self.model = model
        self.ollama_url = ollama_url
        self.inbox_dir = os.path.join(self.base_dir, "inbox")
        self.processed_dir = os.path.join(self.base_dir, "processed")
        self.rejected_dir = os.path.join(self.base_dir, "rejected")
        self.scripts_dir = os.path.join(self.base_dir, "scripts")

        for d in [self.inbox_dir, self.processed_dir, self.rejected_dir, self.scripts_dir]:
            os.makedirs(d, exist_ok=True)

    def extract_python_code(self, response_text):
        match = re.search(r"```python\s*(.*?)\s*```", response_text, re.DOTALL)
        if match:
            return match.group(1)

        match = re.search(r"```\s*(.*?)\s*```", response_text, re.DOTALL)
        if match:
             return match.group(1)

        return response_text

    def process_prompt(self, filename):
        file_path = os.path.join(self.inbox_dir, filename)

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                prompt_content = f.read().strip()

            if not prompt_content:
                console.print(f"[bold red]Empty prompt in {filename}. Rejecting.[/bold red]")
                os.rename(file_path, os.path.join(self.rejected_dir, filename))
                return

            console.print(f"[bold cyan]Processing prompt from: {filename}[/bold cyan]")

            system_prompt = "You are an autonomous coding agent. Write ONLY python code to solve the user's prompt. Do not include explanations, just the raw python code in a markdown block."
            full_prompt = f"{system_prompt}\n\nUser Prompt: {prompt_content}"

            payload = {
                "model": self.model,
                "prompt": full_prompt,
                "stream": False
            }

            response = requests.post(self.ollama_url, json=payload)
            response.raise_for_status()

            result_json = response.json()
            generated_text = result_json.get("response", "")

            code = self.extract_python_code(generated_text)

            output_filename = f"{os.path.splitext(filename)[0]}_output.py"
            output_path = os.path.join(self.scripts_dir, output_filename)

            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(code)

            console.print(f"[bold green]Successfully generated code and saved to {output_path}[/bold green]")

            os.rename(file_path, os.path.join(self.processed_dir, filename))

        except Exception as e:
            console.print(f"[bold red]Error processing {filename}: {str(e)}[/bold red]")
            try:
                os.rename(file_path, os.path.join(self.rejected_dir, filename))
            except Exception as move_error:
                console.print(f"[bold red]Failed to move {filename} to rejected: {str(move_error)}[/bold red]")

    def run(self):
        console.print(f"[bold magenta]Starting Autonomous Coder Swarm watcher on {self.inbox_dir}...[/bold magenta]")
        while True:
            for filename in os.listdir(self.inbox_dir):
                if filename.endswith(".txt"):
                    self.process_prompt(filename)
            time.sleep(2)

if __name__ == "__main__":
    agent = AutonomousCoderSwarm()
    agent.run()
