import requests
import json
import logging
import subprocess
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

OLLAMA_API_URL = "http://localhost:11434/api/chat"
DEFAULT_MODEL = "llama3"

class ChaosEngine:
    def __init__(self, model: str = DEFAULT_MODEL):
        self.model = model
        self.logger = logging.getLogger(__name__)

    def _call_ollama(self, messages: list, temperature: float = 0.7) -> str:
        """Helper to call Ollama chat API."""
        try:
            payload = {
                "model": self.model,
                "messages": messages,
                "stream": False,
                "options": {
                    "temperature": temperature
                }
            }
            response = requests.post(OLLAMA_API_URL, json=payload, timeout=60)
            response.raise_for_status()
            data = response.json()
            return data.get("message", {}).get("content", "")
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Ollama API connection failed: {e}")
            return ""

    def test_connection(self) -> bool:
        """Tests if Ollama is reachable and the model is available."""
        self.logger.info("Testing Ollama connection...")
        response_text = self._call_ollama([{"role": "user", "content": "Say 'hello chaos'"}], temperature=0.1)
        if response_text and "hello" in response_text.lower():
            self.logger.info("Ollama connection successful.")
            return True
        else:
            self.logger.warning("Ollama connection failed or unexpected response.")
            return False

    def generate_mutated_code(self, source_code: str) -> str:
        """Uses Ollama to intentionally inject a subtle logic bug into the source code."""
        self.logger.info("Generating mutated code...")
        system_prompt = (
            "You are a Chaos Engineering AI. Your task is to take the provided Python code and intentionally "
            "inject exactly ONE subtle logic bug into it. The code must still run and not produce syntax errors, "
            "but its behavior should be slightly wrong (e.g., an off-by-one error, wrong boolean operator, "
            "incorrect math operation). Return ONLY the complete mutated python code. "
            "Do not include any explanation or markdown formatting outside the code block itself, "
            "but make sure the code block is wrapped in ```python ... ```."
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Here is the source code to mutate:\n\n{source_code}"}
        ]

        response_text = self._call_ollama(messages, temperature=0.8)

        # Extract code from markdown block
        if "```python" in response_text:
            code = response_text.split("```python")[1].split("```")[0].strip()
        elif "```" in response_text:
            code = response_text.split("```")[1].split("```")[0].strip()
        else:
            code = response_text.strip()

        return code

    def mutate_file(self, target_filepath: Path) -> str:
        """Reads a file, generates a mutated version, and returns the mutated code and original code."""
        if not target_filepath.exists():
            self.logger.error(f"Target file not found: {target_filepath}")
            return "", ""

        original_code = target_filepath.read_text(encoding='utf-8')
        mutated_code = self.generate_mutated_code(original_code)

        if not mutated_code:
            self.logger.error("Failed to generate mutated code.")
            return original_code, ""

        return original_code, mutated_code

    def run_tests(self, test_filepath: Path) -> bool:
        """Runs pytest on the specified test file and returns True if tests pass."""
        self.logger.info(f"Running tests on {test_filepath}...")
        try:
            result = subprocess.run(
                ["pytest", str(test_filepath)],
                capture_output=True,
                text=True,
                timeout=30
            )
            return result.returncode == 0
        except Exception as e:
            self.logger.error(f"Error running pytest: {e}")
            return False

    def generate_augmenting_test(self, original_code: str, mutated_code: str, test_code: str) -> str:
        """Generates a new test to catch the subtle bug introduced in the mutated code."""
        self.logger.info("Generating augmenting test to catch the mutation...")
        system_prompt = (
            "You are a Chaos Engineering AI. You are provided with the original correct code, "
            "a mutated code containing a subtle bug, and the existing test suite that failed to catch it. "
            "Your task is to write exactly ONE new pytest function that passes on the original code "
            "but FAILS on the mutated code, thus catching the bug. "
            "Return ONLY the new python test function code, without any markdown or explanations. "
            "Do NOT include the imports or the original code, JUST the def test_... function block."
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": (
                f"Original Code:\n{original_code}\n\n"
                f"Mutated Code (with bug):\n{mutated_code}\n\n"
                f"Existing Tests:\n{test_code}\n\n"
                "Please generate the new pytest function."
            )}
        ]

        response_text = self._call_ollama(messages, temperature=0.5)

        # Clean up possible markdown
        if "```python" in response_text:
            code = response_text.split("```python")[1].split("```")[0].strip()
        elif "```" in response_text:
            code = response_text.split("```")[1].split("```")[0].strip()
        else:
            code = response_text.strip()

        return code

    def process_target(self, target_filepath: Path, test_filepath: Path) -> dict:
        """
        Main chaos loop:
        1. Read target and test files.
        2. Verify existing tests pass on original code.
        3. Mutate target code.
        4. Run tests. If tests pass, the mutation survived!
        5. If mutation survived, generate a new test to catch it.
        6. Append new test and verify it passes on original code.
        """
        results = {
            "initial_tests_passed": False,
            "mutation_survived": False,
            "new_test_generated": False,
            "new_test_passed": False
        }

        # 1. Verify original tests pass
        if not self.run_tests(test_filepath):
            self.logger.error("Initial tests fail on the original code. Aborting.")
            return results

        results["initial_tests_passed"] = True

        original_code, mutated_code = self.mutate_file(target_filepath)
        if not mutated_code:
            return results

        test_code = test_filepath.read_text(encoding='utf-8')

        # Apply mutation
        self.logger.info("Injecting mutation...")
        target_filepath.write_text(mutated_code, encoding='utf-8')

        try:
            # 2. Run tests on mutated code
            if self.run_tests(test_filepath):
                self.logger.warning("Mutation SURVIVED! The tests failed to catch the bug.")
                results["mutation_survived"] = True

                # 3. Generate augmenting test
                new_test = self.generate_augmenting_test(original_code, mutated_code, test_code)
                if new_test:
                    results["new_test_generated"] = True
                    self.logger.info("Appending new test to test suite...")

                    # Temporarily append the new test
                    updated_test_code = f"{test_code}\n\n{new_test}\n"
                    test_filepath.write_text(updated_test_code, encoding='utf-8')

                    # 4. Restore original code and ensure the new test passes on correct code
                    self.logger.info("Restoring original code...")
                    target_filepath.write_text(original_code, encoding='utf-8')

                    if self.run_tests(test_filepath):
                        self.logger.info("Success! New test passes on the original correct code.")
                        results["new_test_passed"] = True
                    else:
                        self.logger.error("Generated test fails on the original correct code! Reverting test file.")
                        test_filepath.write_text(test_code, encoding='utf-8')
                        results["new_test_passed"] = False
            else:
                self.logger.info("Mutation KILLED! Existing tests caught the bug.")

        finally:
            # Always ensure the original code is restored
            target_filepath.write_text(original_code, encoding='utf-8')

        return results

if __name__ == "__main__":
    engine = ChaosEngine()
    engine.test_connection()
