import json
import urllib.request
import urllib.error
import re
from . import tools
import time

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3" # Default model

SYSTEM_PROMPT = """You are Nexus Core, an autonomous, highly capable agent.
You operate in a ReAct (Reason + Act) loop.

AVAILABLE TOOLS:
- list_files(directory="."): Lists files in the workspace.
- read_file(filepath="name.txt"): Reads the content of a file.
- write_file(filepath="name.txt", content="data"): Writes content to a file.
- python_eval(code="print('hello')"): Executes python code.

INSTRUCTIONS:
You MUST format your output EXACTLY as follows:

Thought: <your reasoning about what to do next>
Action: <tool_name>
Action Input: <the input string for the tool, use JSON if multiple arguments are needed, or raw string if single. For write_file use json: {"filepath": "...", "content": "..."}>

If you have completed the task or cannot proceed, use:
Thought: <final reasoning>
Action: Final Answer
Action Input: <your final response to the user>

EXAMPLES:
Thought: I need to check what files are in the workspace.
Action: list_files
Action Input: .

Thought: I will create a python script.
Action: write_file
Action Input: {"filepath": "script.py", "content": "print('hello world')"}

Thought: I will run the script.
Action: python_eval
Action Input: print('hello world')

Begin!"""

class NexusAgent:
    def __init__(self, log_callback=None):
        self.log_callback = log_callback or (lambda x: None)
        self.is_running = False

    def check_ollama(self):
        try:
            req = urllib.request.Request("http://localhost:11434/api/tags", method="GET")
            with urllib.request.urlopen(req, timeout=2) as response:
                return response.status == 200
        except Exception:
            return False

    def query_ollama(self, prompt: str) -> str:
        data = {
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.2
            }
        }
        req = urllib.request.Request(OLLAMA_URL, data=json.dumps(data).encode('utf-8'),
                                     headers={'Content-Type': 'application/json'})
        try:
            with urllib.request.urlopen(req, timeout=60) as response:
                result = json.loads(response.read().decode('utf-8'))
                return result.get('response', '')
        except urllib.error.URLError as e:
             self.log("Ollama connection failed. Switching to mock mode.")
             return None

    def log(self, message: str, type="info"):
        self.log_callback({"type": type, "message": message, "timestamp": time.time()})

    def parse_action(self, text: str):
        thought_match = re.search(r"Thought:(.*?)(Action:|$)", text, re.DOTALL)
        action_match = re.search(r"Action:(.*?)(Action Input:|$)", text, re.DOTALL)
        input_match = re.search(r"Action Input:(.*?)$", text, re.DOTALL)

        thought = thought_match.group(1).strip() if thought_match else "No thought provided."
        action = action_match.group(1).strip() if action_match else None
        action_input = input_match.group(1).strip() if input_match else ""

        return thought, action, action_input

    def execute_tool(self, action: str, action_input: str):
        try:
            if action == "list_files":
                return tools.list_files(action_input or ".")
            elif action == "read_file":
                return tools.read_file(action_input)
            elif action == "write_file":
                try:
                    data = json.loads(action_input)
                    return tools.write_file(data['filepath'], data['content'])
                except json.JSONDecodeError:
                    return "Error: Action Input for write_file must be valid JSON: {\"filepath\": \"...\", \"content\": \"...\"}"
            elif action == "python_eval":
                return tools.python_eval(action_input)
            elif action == "Final Answer":
                return "SUCCESS"
            else:
                return f"Error: Unknown tool '{action}'."
        except Exception as e:
            return f"Error executing tool '{action}': {str(e)}"

    def run(self, task: str):
        self.is_running = True
        self.log(f"Starting Task: {task}", type="start")

        if not self.check_ollama():
            self.log("Ollama not found at localhost:11434. Running MOCK agent simulation.", type="warning")
            self._run_mock_loop(task)
            self.is_running = False
            return

        history = f"{SYSTEM_PROMPT}\n\nUser Task: {task}\n"
        max_steps = 10
        step = 0

        while step < max_steps and self.is_running:
            self.log(f"Agent thinking (Step {step + 1}/{max_steps})...", type="system")
            response = self.query_ollama(history)

            if response is None:
                self.log("Failed to get response from Ollama.", type="error")
                break

            history += response + "\n"

            thought, action, action_input = self.parse_action(response)

            self.log(f"{thought}", type="thought")

            if action == "Final Answer":
                self.log(f"{action_input}", type="final")
                break

            if action:
                self.log(f"Executing: {action}({action_input})", type="action")
                tool_result = self.execute_tool(action, action_input)
                self.log(f"Result: {tool_result}", type="result")
                history += f"Observation: {tool_result}\n"
            else:
                self.log("No valid action parsed. Retrying.", type="warning")
                history += "Observation: You must provide an Action and Action Input.\n"

            step += 1

        if step >= max_steps:
            self.log("Max steps reached. Terminating task.", type="error")

        self.is_running = False

    def _run_mock_loop(self, task: str):
        """Simulates agent behavior when Ollama is not available."""
        time.sleep(1)
        self.log("I need to analyze the task.", type="thought")
        time.sleep(1)

        self.log("list_files(.)", type="action")
        res = tools.list_files(".")
        self.log(res, type="result")
        time.sleep(1)

        self.log("I will write a mock script to fulfill the task.", type="thought")
        time.sleep(1)

        mock_code = "print('Mock script executed for task: " + task.replace("'", "\\'") + "')"
        self.log("write_file({\"filepath\": \"mock.py\", \"content\": \"...\"})", type="action")
        res = tools.write_file("mock.py", mock_code)
        self.log(res, type="result")
        time.sleep(1)

        self.log("I will run the mock script.", type="thought")
        time.sleep(1)

        self.log("python_eval(mock.py contents)", type="action")
        res = tools.python_eval(mock_code)
        self.log(res, type="result")
        time.sleep(1)

        self.log("Task completed successfully in mock mode.", type="thought")
        self.log("Task finished.", type="final")
