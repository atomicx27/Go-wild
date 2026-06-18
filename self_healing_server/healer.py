import re
import os
import httpx
import traceback
from patcher import apply_diff

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434/api/generate")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3")

def extract_file_from_traceback(tb_str: str) -> str:
    """Extracts the innermost file path from our project causing the error."""
    # Look for files in our directory, skipping site-packages or standard library
    lines = tb_str.split('\n')
    target_file = None
    for line in reversed(lines):
        match = re.search(r'File "(.*?)", line \d+', line)
        if match:
            filepath = match.group(1)
            # Only fix files within our current working directory to be safe
            if os.path.abspath(filepath).startswith(os.getcwd()) and "site-packages" not in filepath and "lib" not in filepath:
                target_file = filepath
                break
    return target_file

async def heal_code(tb_str: str):
    """Analyzes traceback, asks Ollama for fix, and applies it."""
    print("🤖 Analyzing error traceback...")
    target_file = extract_file_from_traceback(tb_str)

    if not target_file:
        print("❌ Could not determine target file from traceback.")
        return

    print(f"🎯 Target file identified: {target_file}")

    try:
        with open(target_file, "r") as f:
            source_code = f.read()
    except Exception as e:
        print(f"❌ Failed to read target file {target_file}: {e}")
        return

    prompt = f"""You are an autonomous self-healing code agent.
An exception occurred in the following Python file: {target_file}

Here is the traceback:
```
{tb_str}
```

Here is the current source code of {target_file}:
```python
{source_code}
```

Please analyze the error and provide a fix.
IMPORTANT: Your output MUST contain exactly ONE valid git merge conflict diff format block that fixes the issue.
Do not provide multiple diff blocks. Do not explain anything outside the diff block.
The diff block format is:
<<<<<<< SEARCH
[Exact lines from the original file to replace]
=======
[New lines to insert]
>>>>>>> REPLACE

Make sure the SEARCH block matches the original file exactly.

Fix:
"""

    print(f"🧠 Asking Ollama ({OLLAMA_MODEL}) for a fix...")
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                OLLAMA_URL,
                json={
                    "model": OLLAMA_MODEL,
                    "prompt": prompt,
                    "stream": False
                }
            )
            response.raise_for_status()
            result = response.json()
            llm_response = result.get("response", "")

            print(f"✨ Received patch from Ollama. Applying...")
            success = apply_diff(target_file, source_code, llm_response)
            if success:
                print(f"✅ Successfully patched {target_file}! The server should handle requests better now.")
            else:
                print(f"⚠️ Failed to apply patch to {target_file}.")

    except Exception as e:
        print(f"❌ Failed to communicate with Ollama or apply patch: {e}")
        traceback.print_exc()
