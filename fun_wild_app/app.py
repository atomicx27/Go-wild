import subprocess
import json
import time

def generate_idea():
    prompt = "Give me one totally wild, funny, and creative idea for a mini python script I can run right now. It can be anything from a silly ascii art generator, to a weird text game, to a poetic response generator. Just give me the description of what it should do, nothing else. Make it maximum two sentences."
    print(f"Asking Ollama to think of an idea...")

    data = {
        "model": "qwen2.5:7b",
        "prompt": prompt,
        "stream": False
    }

    response = subprocess.run(
        ["curl", "-s", "-X", "POST", "http://localhost:11434/api/generate", "-d", json.dumps(data)],
        capture_output=True, text=True
    )

    try:
        result = json.loads(response.stdout)
        return result.get("response", "Error generating idea").strip()
    except:
        return "Error: Could not parse idea."

def write_code(idea):
    prompt = f"Write a complete, single-file Python script that does this: '{idea}'. Ensure it is fully self-contained and only outputs the python code. Do not include markdown formatting like ```python, just the raw code. DO NOT wrap the code in backticks or any markdown. Just the code."

    print(f"Asking Ollama to write the code...")

    data = {
        "model": "qwen2.5:7b",
        "prompt": prompt,
        "stream": False
    }

    response = subprocess.run(
        ["curl", "-s", "-X", "POST", "http://localhost:11434/api/generate", "-d", json.dumps(data)],
        capture_output=True, text=True
    )

    try:
        result = json.loads(response.stdout)
        code = result.get("response", "").strip()
        if code.startswith("```python"):
            code = code[9:]
        if code.startswith("```"):
            code = code[3:]
        if code.endswith("```"):
            code = code[:-3]
        return code.strip()
    except:
        return "print('Error: Could not parse code.')"

if __name__ == "__main__":
    print("Welcome to the Wild Idea Generator & Executor!\n")
    idea = generate_idea()
    print(f"\nHere is the wild idea:\n{idea}\n")

    code = write_code(idea)

    print("\nHere is the generated code:")
    print("-" * 40)
    print(code)
    print("-" * 40)

    with open("wild_script.py", "w") as f:
        f.write(code)

    print("\nRunning the wild script now...\n")
    time.sleep(1)

    result = subprocess.run(["python3", "wild_script.py"], capture_output=True, text=True)

    print(result.stdout)
    if result.stderr:
        print("ERRORS:")
        print(result.stderr)
