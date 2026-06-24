import os
import re
from openai import AsyncOpenAI
import asyncio

OLLAMA_API_BASE = "http://localhost:11434/v1"
MODEL_NAME = "qwen2.5:0.5b"
WORKSPACE_DIR = os.path.join(os.path.dirname(__file__), "workspace")

client = AsyncOpenAI(
    base_url=OLLAMA_API_BASE,
    api_key="ollama"  # Required but ignored by ollama
)

SYSTEM_PROMPT = """You are an autonomous expert software engineer.
The user will ask you to build something or write code.
You must think, plan, and then output code files.
When you output a file, you MUST start the code block EXACTLY like this:
```[filename]
For example:
```main.py
print("Hello World")
```
Never use "```python". Always put the actual filename right after the backticks.
"""

async def run_agent(prompt: str, callback=None):
    if not os.path.exists(WORKSPACE_DIR):
        os.makedirs(WORKSPACE_DIR)

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": prompt}
    ]

    if callback:
        await callback(f"Thinking about: {prompt}...")

    response = await client.chat.completions.create(
        model=MODEL_NAME,
        messages=messages,
    )

    content = response.choices[0].message.content

    if callback:
        await callback("I have generated a response. Parsing files...")

    pattern = re.compile(r"```(.*?)?\n(.*?)```", re.DOTALL)
    matches = pattern.findall(content)

    saved_files = []

    # We will try to find a file name from the user prompt as a fallback if the model fails
    expected_files = re.findall(r"([a-zA-Z0-9_\-]+\.(?:py|js|html|css|txt|md))", prompt)
    default_filename = expected_files[0] if expected_files else "generated.txt"

    for filename, file_content in matches:
        filename = filename.strip()
        if not filename or filename.lower() in ["python", "html", "javascript", "js", "css", "bash", "sh"]:
            filename = default_filename

        filepath = os.path.join(WORKSPACE_DIR, filename)
        with open(filepath, "w") as f:
            f.write(file_content.strip())
        saved_files.append(filename)
        if callback:
            await callback(f"Wrote file: {filename}")

    if not saved_files:
        if callback:
            await callback("No files were formatted correctly to be saved.")

    if callback:
        await callback("I have finished processing.")

    return saved_files, content

if __name__ == "__main__":
    async def main():
        await run_agent("Create a simple Python script called hello.py that prints hello world.")
    asyncio.run(main())
