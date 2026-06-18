import subprocess
import time
import requests
import os
import signal

def main():
    print("🚀 Starting Self-Healing Server Demo")

    # Start Mock Ollama
    print("Starting Mock Ollama on port 11434...")
    mock_env = os.environ.copy()
    mock_process = subprocess.Popen(
        ["python3", "mock_ollama.py"],
        env=mock_env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    # Start Main App
    print("Starting Main FastAPI App on port 8000...")
    app_env = os.environ.copy()
    app_process = subprocess.Popen(
        ["python3", "main.py"],
        env=app_env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )

    time.sleep(3) # Wait for servers to spin up

    print("\n--- Testing Healthy Route ---")
    resp = requests.get("http://localhost:8000/hello")
    print(f"Status: {resp.status_code}")
    print(f"Response: {resp.json()}")

    print("\n--- Triggering Bug: Division By Zero ---")
    resp = requests.get("http://localhost:8000/divide?a=10&b=0")
    print(f"Status: {resp.status_code}")
    print(f"Response: {resp.json()}")

    print("\n⏳ Waiting 5 seconds for background healing agent to patch code and hot-reload...")
    time.sleep(5)

    print("\n--- Retrying Buggy Route ---")
    resp = requests.get("http://localhost:8000/divide?a=10&b=0")
    print(f"Status: {resp.status_code}")
    print(f"Response: {resp.json()}")

    print("\n--- Triggering Bug: Text Append ---")
    resp = requests.get("http://localhost:8000/concat?text=hi&times=3")
    print(f"Status: {resp.status_code}")
    print(f"Response: {resp.json()}")

    print("\n⏳ Waiting 5 seconds for background healing agent to patch code and hot-reload...")
    time.sleep(5)

    print("\n--- Retrying Buggy Route ---")
    resp = requests.get("http://localhost:8000/concat?text=hi&times=3")
    print(f"Status: {resp.status_code}")
    print(f"Response: {resp.json()}")

    print("\nCleaning up processes...")
    app_process.terminate()
    mock_process.terminate()
    app_process.wait()
    mock_process.wait()

    # Restore original buggy_routes.py for next run
    print("Restoring original buggy_routes.py...")
    with open("buggy_routes.py", "w") as f:
        f.write('''from fastapi import APIRouter

router = APIRouter()

@router.get("/divide")
async def divide(a: int, b: int):
    # Intentional bug: Does not handle division by zero
    result = a / b
    return {"result": result}

@router.get("/concat")
async def concat(text: str, times: int):
    # Intentional bug: Cannot concatenate str and int if user sends wrong type or if python interprets something poorly
    # Or simple typo bug to be fixed
    # Actually, let's make a real bug: trying to use list method on string
    result = text.append("!")
    return {"result": result}

@router.get("/hello")
async def hello():
    return {"message": "Hello, world! Server is alive."}
''')

    print("Demo complete!")

if __name__ == "__main__":
    main()
