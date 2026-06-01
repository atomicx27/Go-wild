import os
import json
import time
import subprocess
import re
import shutil
from pathlib import Path
import logging

from cyber_forge.llm_client import chat_with_ollama, extract_code_blocks
from cyber_forge.html_builder import build_armory_html

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent
INBOX_DIR = BASE_DIR / "inbox"
ARMORY_DIR = BASE_DIR / "armory"
MAX_HEALING_ATTEMPTS = 5

def initialize():
    """Ensure directories exist and initial UI is built."""
    INBOX_DIR.mkdir(parents=True, exist_ok=True)
    ARMORY_DIR.mkdir(parents=True, exist_ok=True)
    build_armory_html(ARMORY_DIR)

def generate_tool_code(idea_text):
    """Prompt LLM to generate the Python tool code."""
    messages = [
        {"role": "system", "content": "You are a master python developer. Write exactly what is asked. Provide ONLY the python code inside ```python blocks. Do not explain."},
        {"role": "user", "content": f"Write a standalone python script that does the following. It should not require any external dependencies outside of standard library if possible, unless strictly necessary.\n\nIdea: {idea_text}"}
    ]
    response = chat_with_ollama(messages)
    return extract_code_blocks(response, "python")

def generate_test_code(tool_code):
    """Prompt LLM to generate a pytest suite for the tool."""
    messages = [
        {"role": "system", "content": "You are a master python QA engineer. Write a complete pytest test suite for the provided code. Provide ONLY the python test code inside ```python blocks. Do not explain."},
        {"role": "user", "content": f"Write a pytest suite to comprehensively test this code:\n\n```python\n{tool_code}\n```\n\nEnsure it handles edge cases. Assume the code is in a file named `tool.py` and import from it like `import tool` or `from tool import ...`"}
    ]
    response = chat_with_ollama(messages)
    return extract_code_blocks(response, "python")

def self_heal(tool_code, test_code, error_output):
    """Prompt LLM to fix the code or tests based on the error output."""
    messages = [
        {"role": "system", "content": "You are a master python developer and QA engineer. The tests failed. Fix EITHER the tool code OR the test code to make them pass. Provide your response as a JSON object with 'tool_code' and 'test_code' keys containing the complete fixed python code for both. Do not use markdown blocks in the JSON values, just the raw string."},
        {"role": "user", "content": f"The following tests failed.\n\nTool Code:\n```python\n{tool_code}\n```\n\nTest Code:\n```python\n{test_code}\n```\n\nError Output:\n```\n{error_output}\n```\n\nProvide the fixed codes in JSON format."}
    ]
    response = chat_with_ollama(messages)

    # Try to parse the JSON response
    try:
        # Extract JSON if it's wrapped in markdown
        json_str = response
        if "```json" in response:
            json_str = response.split("```json")[1].split("```")[0]
        elif "```" in response:
            json_str = response.split("```")[1].split("```")[0]

        fixed = json.loads(json_str.strip())
        return fixed.get("tool_code", tool_code), fixed.get("test_code", test_code)
    except Exception as e:
        logger.error(f"Failed to parse healing response as JSON: {e}")
        # Fallback heuristic: try to extract python blocks and guess which is which
        blocks = re.findall(r"```python\n(.*?)```", response, re.DOTALL)
        if len(blocks) >= 2:
            return blocks[0], blocks[1]
        return tool_code, test_code

def test_tool(workspace_dir, tool_code, test_code):
    """Run pytest on the tool in an isolated workspace."""
    tool_file = workspace_dir / "tool.py"
    test_file = workspace_dir / "test_tool.py"

    tool_file.write_text(tool_code, encoding='utf-8')
    test_file.write_text(test_code, encoding='utf-8')

    try:
        # Run pytest
        result = subprocess.run(
            ["python3", "-m", "pytest", str(test_file)],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=str(workspace_dir)
        )
        return result.returncode == 0, result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        return False, "Test execution timed out after 30 seconds."
    except Exception as e:
        return False, f"Execution error: {e}"

def process_idea(idea_file: Path):
    """Process a single idea file through the agentic loop."""
    idea_name = idea_file.stem
    idea_text = idea_file.read_text(encoding='utf-8')

    logger.info(f"Forging new tool: {idea_name}")

    # Create temporary workspace
    workspace = BASE_DIR / f"temp_{idea_name}"
    workspace.mkdir(exist_ok=True)

    try:
        # Initial Generation
        logger.info("Generating initial code...")
        tool_code = generate_tool_code(idea_text)
        if not tool_code:
            logger.error("Failed to generate tool code.")
            return False

        logger.info("Generating initial tests...")
        test_code = generate_test_code(tool_code)
        if not test_code:
            logger.error("Failed to generate test code.")
            return False

        # Self-Healing Loop
        attempts = 0
        success = False

        while attempts < MAX_HEALING_ATTEMPTS:
            attempts += 1
            logger.info(f"Running tests (Attempt {attempts}/{MAX_HEALING_ATTEMPTS})...")

            passed, output = test_tool(workspace, tool_code, test_code)

            if passed:
                logger.info(f"Tests passed on attempt {attempts}!")
                success = True
                break

            logger.warning(f"Tests failed. Initiating self-healing...")
            tool_code, test_code = self_heal(tool_code, test_code, output)

        # If successful, move to armory
        if success:
            logger.info(f"Forging complete. Moving {idea_name} to Armory.")
            final_tool_file = f"{idea_name}.py"
            final_test_file = f"test_{idea_name}.py"

            (ARMORY_DIR / final_tool_file).write_text(tool_code, encoding='utf-8')
            (ARMORY_DIR / final_test_file).write_text(test_code, encoding='utf-8')

            metadata = {
                "name": idea_name.replace("_", " ").title(),
                "description": idea_text.strip()[:200] + ("..." if len(idea_text) > 200 else ""),
                "attempts": attempts,
                "code_file": final_tool_file,
                "test_file": final_test_file
            }

            (ARMORY_DIR / f"{idea_name}.json").write_text(json.dumps(metadata, indent=2), encoding='utf-8')

            # Rebuild UI
            build_armory_html(ARMORY_DIR)

            # Remove idea file from inbox
            idea_file.unlink()
            return True
        else:
            logger.error(f"Failed to forge {idea_name} after {MAX_HEALING_ATTEMPTS} attempts.")
            # Rename failed idea to prevent infinite looping
            idea_file.rename(idea_file.with_suffix(".failed"))
            return False

    finally:
        # Cleanup workspace
        if workspace.exists():
            shutil.rmtree(workspace)

def run_forge_loop():
    """Main daemon loop to watch the inbox."""
    initialize()
    logger.info("Cyber Forge activated. Watching inbox...")

    try:
        while True:
            for idea_file in INBOX_DIR.glob("*.txt"):
                process_idea(idea_file)
            time.sleep(2)
    except KeyboardInterrupt:
        logger.info("Cyber Forge shutting down.")

if __name__ == "__main__":
    run_forge_loop()
