import os
import sys
import subprocess
import json
import urllib.request
import urllib.error

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434/api/generate")
MODEL = os.environ.get("OLLAMA_MODEL", "qwen2.5:0.5b")

def query_ollama(prompt, format_json=False):
    data = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False
    }
    if format_json:
        data["format"] = "json"

    req = urllib.request.Request(OLLAMA_URL, data=json.dumps(data).encode('utf-8'), headers={'Content-Type': 'application/json'})

    try:
        response = urllib.request.urlopen(req)
        result = json.loads(response.read().decode('utf-8'))
        return result.get("response", "")
    except Exception as e:
        print(f"Error querying Ollama: {e}")
        return None

def execute_command(command):
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr
        }
    except Exception as e:
         return {
            "success": False,
            "stdout": "",
            "stderr": str(e)
        }

def chat():
    print("Terminal Assistant (type 'exit' to quit)")
    print("-" * 40)

    # Very simple context
    history = []

    while True:
        try:
            user_input = input("You> ")
            if user_input.lower() in ['exit', 'quit']:
                break

            prompt = f"""You are a helpful terminal assistant. The user will ask you questions or give you tasks.
If the user wants you to execute a bash command, return ONLY a JSON object with the key "command" containing the command to run.
If you just want to reply with text, return ONLY a JSON object with the key "reply".

User input: {user_input}
History: {history}
"""
            response_str = query_ollama(prompt, format_json=True)
            if not response_str:
                continue

            try:
                response = json.loads(response_str)
                if "command" in response:
                    cmd = response["command"]
                    print(f"Assistant> Executing: {cmd}")

                    # Ask for confirmation before running
                    confirm = input("Run this command? (y/N): ")
                    if confirm.lower() == 'y':
                        res = execute_command(cmd)
                        output = res['stdout'] if res['success'] else res['stderr']
                        print(f"Output:\n{output}")
                        history.append({"user": user_input, "command": cmd, "result": output})
                    else:
                        print("Assistant> Command cancelled.")
                        history.append({"user": user_input, "cancelled_command": cmd})

                elif "reply" in response:
                    reply = response["reply"]
                    print(f"Assistant> {reply}")
                    history.append({"user": user_input, "reply": reply})
                else:
                    print(f"Assistant (raw)> {response_str}")

            except json.JSONDecodeError:
                print(f"Assistant (raw)> {response_str}")

        except EOFError:
            break
        except KeyboardInterrupt:
            break

if __name__ == "__main__":
    chat()
