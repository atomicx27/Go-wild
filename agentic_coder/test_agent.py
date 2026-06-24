import asyncio
import os
from agent import run_agent, WORKSPACE_DIR

async def mock_callback(msg):
    print(f"[Callback] {msg}")

async def main():
    prompt = "Create a simple python file named math_test.py that defines an add function."
    print(f"Running agent with prompt: {prompt}")
    saved_files, raw_response = await run_agent(prompt, callback=mock_callback)

    print("\n--- Summary ---")
    print(f"Saved files: {saved_files}")

    if "math_test.py" in saved_files:
        filepath = os.path.join(WORKSPACE_DIR, "math_test.py")
        if os.path.exists(filepath):
            with open(filepath, "r") as f:
                content = f.read()
            print(f"\n--- Content of math_test.py ---\n{content}")
            print("\nTest PASSED!")
        else:
            print("\nTest FAILED: File reported as saved but not found on disk.")
    else:
        print("\nTest FAILED: math_test.py was not saved by the agent.")

if __name__ == "__main__":
    asyncio.run(main())
