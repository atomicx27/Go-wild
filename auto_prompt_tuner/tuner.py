import requests
import json
import re
from typing import List, Dict, Tuple
from rich.console import Console

console = Console()

class AutoPromptTuner:
    def __init__(self, model: str = "qwen2.5:0.5b", base_url: str = "http://localhost:11434"):
        self.model = model
        self.base_url = base_url
        self.api_url = f"{self.base_url}/api/generate"

    def call_ollama(self, prompt: str) -> str:
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False
        }
        try:
            response = requests.post(self.api_url, json=payload, timeout=60)
            response.raise_for_status()
            return response.json().get("response", "").strip()
        except Exception as e:
            console.print(f"[bold red]Error calling Ollama:[/] {e}")
            return ""

    def evaluate_prompt(self, prompt: str, test_cases: List[Dict[str, str]]) -> float:
        """Evaluates a prompt against a list of test cases (input -> expected_output)."""
        score = 0
        total = len(test_cases)
        for case in test_cases:
            input_text = case["input"]
            expected_output = case["expected_output"]

            # Combine the instruction prompt with the input data
            full_prompt = f"{prompt}\n\nInput:\n{input_text}"

            output = self.call_ollama(full_prompt)

            # Simple exact match evaluation for now. Could be improved with LLM-as-a-judge
            if expected_output.lower() in output.lower():
                score += 1

        return score / total if total > 0 else 0

    def mutate_prompt(self, current_prompt: str, failures: List[Dict[str, str]]) -> List[str]:
        """Generates variations of the current prompt based on failures."""
        mutation_prompt = f"""
You are an expert prompt engineer. I have a prompt that is not performing perfectly.
Here is the current prompt:
"{current_prompt}"

Here are some examples where it failed (the output did not match the expected):
"""
        for fail in failures:
            mutation_prompt += f"- Input: {fail['input']}\n  Expected: {fail['expected_output']}\n  Actual: {fail['actual_output']}\n"

        mutation_prompt += """
Please provide 3 new, distinct variations of this prompt that might perform better.
Make them diverse (e.g., one very detailed, one very concise, one with examples).
Output ONLY the 3 prompts, separated by "---PROMPT_SEPARATOR---". Do not include any other text.
"""
        response = self.call_ollama(mutation_prompt)

        # Parse the response
        mutations = [p.strip() for p in response.split("---PROMPT_SEPARATOR---") if p.strip()]

        # Fallback if the LLM didn't use the separator correctly
        if not mutations or len(mutations) == 1:
            # Try to extract numbered lists or just use the whole response as one mutation
            lines = response.split('\n')
            mutations = []
            current = []
            for line in lines:
                if re.match(r'^\d+\.', line.strip()) or line.strip().startswith('-'):
                    if current:
                        mutations.append('\n'.join(current).strip())
                        current = []
                current.append(line)
            if current:
                mutations.append('\n'.join(current).strip())

            # Clean up leading numbers/dashes
            mutations = [re.sub(r'^(\d+\.|-)\s*', '', m).strip() for m in mutations]

        # Filter out empty strings and return up to 3
        return [m for m in mutations if m][:3]

    def optimize(self, initial_prompt: str, test_cases: List[Dict[str, str]], iterations: int = 3) -> str:
        best_prompt = initial_prompt
        best_score = self.evaluate_prompt(best_prompt, test_cases)

        console.print(f"[bold cyan]Initial Prompt:[/] {best_prompt} (Score: {best_score})")

        if best_score == 1.0:
            console.print("[bold green]Initial prompt is already perfect![/]")
            return best_prompt

        current_prompt = best_prompt

        for i in range(iterations):
            console.print(f"\n[bold yellow]--- Iteration {i+1} ---[/]")

            # Collect failures for the current prompt
            failures = []
            for case in test_cases:
                full_prompt = f"{current_prompt}\n\nInput:\n{case['input']}"
                output = self.call_ollama(full_prompt)
                if case['expected_output'].lower() not in output.lower():
                    failures.append({
                        "input": case["input"],
                        "expected_output": case["expected_output"],
                        "actual_output": output
                    })

            if not failures:
                console.print("[bold green]Perfect score achieved![/]")
                break

            console.print(f"Generating mutations based on {len(failures)} failures...")
            candidates = self.mutate_prompt(current_prompt, failures)

            if not candidates:
                 console.print("[yellow]No mutations generated. Sticking with current best.[/]")
                 continue

            for idx, candidate in enumerate(candidates):
                score = self.evaluate_prompt(candidate, test_cases)
                console.print(f"Candidate {idx+1} Score: {score} | Prompt snippet: {candidate[:50]}...")

                if score > best_score:
                    best_score = score
                    best_prompt = candidate
                    console.print(f"[bold green]New Best Prompt Found![/] (Score: {best_score})")

            current_prompt = best_prompt

            if best_score == 1.0:
                break

        console.print(f"\n[bold magenta]Final Optimized Prompt:[/] {best_prompt} (Score: {best_score})")
        return best_prompt

if __name__ == "__main__":
    tuner = AutoPromptTuner()

    # Simple test dataset for translation with a difficult translation
    test_data = [
        {"input": "Hello", "expected_output": "Bonjour"},
        {"input": "I am eating an apple", "expected_output": "Je mange une pomme"},
        {"input": "It is raining cats and dogs", "expected_output": "Il pleut des cordes"}
    ]

    initial = "Translate this phrase:"

    tuner.optimize(initial, test_data, iterations=2)
