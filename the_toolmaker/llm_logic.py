import json
import re
import os
from .ollama_client import chat
from .registry import format_registry_for_llm, add_tool

def analyze_request(user_request):
    """
    Analyzes the user's request and determines if a new tool is needed
    or if an existing one can be used.
    """
    registry_str = format_registry_for_llm()

    prompt = f"""
You are an autonomous agent capable of writing Python scripts to solve tasks.
You have a registry of existing tools you have written before.

User Request: "{user_request}"

{registry_str}

Analyze the user request and determine the best course of action.
You MUST output a JSON object in the following format inside a markdown block:

```json
{{
    "action": "use_existing" | "create_new",
    "tool_name": "name_of_existing_tool_or_new_tool",
    "reasoning": "Why you chose this action."
}}
```

If the user request can be fully solved by an existing tool (perhaps with different arguments), choose "use_existing".
If no existing tool is suitable, choose "create_new" and provide a descriptive name for the new tool (e.g., "string_reverser").
"""

    response = chat(prompt)

    # Extract JSON block
    json_match = re.search(r'```json\n(.*?)\n```', response, re.DOTALL)

    # Fallback to mock logic if the JSON format fails (e.g. mock ollama response)
    if not json_match:
        print("[LLM Logic] Could not parse JSON from analysis. Falling back to creating new tool.")
        return {
            "action": "create_new",
            "tool_name": "fallback_tool",
            "reasoning": "Failed to parse analysis response."
        }

    try:
        data = json.loads(json_match.group(1))
        return data
    except json.JSONDecodeError:
        print("[LLM Logic] JSON decode error in analysis.")
        return {
             "action": "create_new",
             "tool_name": "fallback_tool",
             "reasoning": "JSON parsing error."
        }

def forge_tool(tool_name, user_request):
    """
    Asks the LLM to write a new Python tool to solve the user's request.
    Saves the tool and adds it to the registry.
    """
    filename = f"{tool_name}.py"
    filepath = os.path.join(os.path.dirname(__file__), "tools", filename)
    relative_filepath = f"the_toolmaker/tools/{filename}"

    prompt = f"""
You need to write a pure Python script to fulfill the following user request: "{user_request}"

Requirements:
1. The script must be self-contained and run from the command line.
2. It should use `argparse` or `sys.argv` to accept inputs if necessary.
3. The script will be saved as `{filename}`.
4. Output ONLY the python code inside a markdown block. Do not include any other text.
5. Provide a brief docstring explaining what the tool does.

Example output format:
```python
import sys

def main():
    print("Hello", sys.argv[1])

if __name__ == "__main__":
    main()
```
"""

    response = chat(prompt)

    # Extract python code block
    code_match = re.search(r'```python\n(.*?)\n```', response, re.DOTALL)

    if not code_match:
        # Check if the code was provided without markdown blocks
        if "import " in response or "def " in response:
            code = response
        else:
             print("[LLM Logic] Failed to extract python code from response.")
             return None
    else:
        code = code_match.group(1)

    # Save the tool
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(code)

    print(f"[Toolmaker] Forged new tool: {filepath}")

    # Generate description and usage for registry
    desc_prompt = f"Summarize what this python script does in one sentence:\n\n{code}"
    description = chat(desc_prompt).strip()

    usage_example = f"python {relative_filepath} <args>"

    add_tool(tool_name, description, relative_filepath, usage_example)
    return relative_filepath

def plan_execution(tool_filepath, user_request):
    """
    Asks the LLM to provide the exact bash command to run the tool for the specific request.
    """
    prompt = f"""
You need to generate the exact bash command to run a Python script to fulfill the user's request.

User Request: "{user_request}"
Tool Filepath: "{tool_filepath}"

Output ONLY the exact bash command required. No markdown formatting, no explanations.
Assume `python3` is the executable.

For example, if the tool reverses strings and the user wants to reverse "hello", output:
python3 {tool_filepath} "hello"
"""

    response = chat(prompt).strip()

    # Clean up response if the LLM adds backticks anyway
    response = response.replace('```bash', '').replace('```python', '').replace('```', '').strip()

    # If it has line breaks, just grab the first line to be safe, unless it's a mock script
    lines = [line.strip() for line in response.split('\n') if line.strip()]
    for line in lines:
        if line.startswith('python'):
            return line

    # Fallback if no clean python command was generated
    return f"python3 {tool_filepath}"
