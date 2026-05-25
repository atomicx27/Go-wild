import json
import urllib.request
import urllib.error
import os
import re
from pathlib import Path

class Architect:
    def __init__(self, output_dir="system_architect/blueprints", model="llama3"):
        self.output_dir = Path(output_dir)
        self.model = model
        self.api_url = "http://localhost:11434/api/chat"

    def _query_ollama(self, prompt):
        system_message = """You are an expert system architect and project scaffolder.
Your task is to take a user's prompt describing a project and generate a complete, optimal directory and file structure with starter code.

You MUST respond with a SINGLE valid JSON object and NOTHING else.
Do not add any conversational text before or after the JSON.

The JSON object must have this exact schema:
{
  "dirs": [
    "string representing directory path relative to project root"
  ],
  "files": [
    {
      "path": "string representing file path relative to project root",
      "content": "string containing the complete starter code for the file"
    }
  ]
}

Example:
{
  "dirs": ["src", "tests"],
  "files": [
    {"path": "src/main.py", "content": "def main():\n    print('hello')\n\nif __name__ == '__main__':\n    main()"},
    {"path": "tests/test_main.py", "content": "def test_main():\n    assert True"}
  ]
}
"""
        data = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ],
            "stream": False
        }

        req = urllib.request.Request(
            self.api_url,
            data=json.dumps(data).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )

        try:
            with urllib.request.urlopen(req) as response:
                result = json.loads(response.read().decode("utf-8"))
                return result["message"]["content"]
        except urllib.error.URLError as e:
            raise RuntimeError(f"Failed to connect to Ollama: {e}")

    def _extract_json(self, text):
        # Try to find a JSON block in the text
        # It could be wrapped in ```json ... ``` or just be the text itself

        # Strip markdown code blocks if present
        text = text.strip()
        if text.startswith("```json"):
            text = text[7:]
        elif text.startswith("```"):
            text = text[3:]

        if text.endswith("```"):
            text = text[:-3]

        text = text.strip()

        # Sometimes LLM might have text before or after the JSON braces
        # We try to extract everything from the first '{' to the last '}'
        start_idx = text.find('{')
        end_idx = text.rfind('}')
        if start_idx != -1 and end_idx != -1 and end_idx >= start_idx:
            text = text[start_idx:end_idx+1]

        return json.loads(text)

    def generate_blueprint(self, prompt):
        print(f"\033[36m[Architect]\033[0m Querying Ollama for blueprint: '{prompt}'")
        raw_response = self._query_ollama(prompt)
        try:
            blueprint = self._extract_json(raw_response)
            return blueprint
        except json.JSONDecodeError as e:
            print(f"\033[31m[Architect Error]\033[0m Failed to parse JSON response: {e}")
            print(f"\033[33mRaw Response:\033[0m\n{raw_response}")
            raise

    def build_blueprint(self, blueprint, project_name):
        base_path = self.output_dir / project_name

        print(f"\033[32m[Architect]\033[0m Building project '{project_name}' in {base_path}")

        # Create base directory
        base_path.mkdir(parents=True, exist_ok=True)

        resolved_base_path = base_path.resolve()

        # Create directories
        dirs = blueprint.get("dirs", [])
        for d in dirs:
            dir_path = (base_path / d).resolve()
            if not dir_path.is_relative_to(resolved_base_path):
                print(f"  \033[31m- Skipped Directory (Path Traversal attempt):\033[0m {d}")
                continue
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"  \033[90m+ Directory:\033[0m {d}")

        # Create files
        files = blueprint.get("files", [])
        for f in files:
            file_path = (base_path / f.get("path", "")).resolve()
            if not file_path.name:
                continue
            if not file_path.is_relative_to(resolved_base_path):
                print(f"  \033[31m- Skipped File (Path Traversal attempt):\033[0m {f.get('path', '')}")
                continue

            # Ensure parent directories exist just in case
            file_path.parent.mkdir(parents=True, exist_ok=True)

            with open(file_path, "w", encoding="utf-8") as out_f:
                out_f.write(f.get("content", ""))
            print(f"  \033[94m+ File:\033[0m {f.get('path', '')}")

        print(f"\033[32m[Architect]\033[0m Project '{project_name}' successfully scaffolded!")
        return base_path

    def run(self, prompt, project_name):
        blueprint = self.generate_blueprint(prompt)
        return self.build_blueprint(blueprint, project_name)
