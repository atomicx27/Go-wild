import re
import sys
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from prompt_toolkit import PromptSession
from prompt_toolkit.styles import Style

from .client import OllamaClient
from .executor import CommandExecutor

console = Console()

SYSTEM_PROMPT = """You are an advanced, autonomous AI assistant running in a command-line environment.
You have the ability to execute shell commands on the user's machine to fulfill their requests.

You MUST respond using ONE of the following two formats:

1. If you need to execute a command to gather information or perform an action, respond with:
<THINK>
Your internal reasoning about what command to run and why.
</THINK>
<EXECUTE>
the_shell_command_here
</EXECUTE>

2. If you have gathered enough information and are ready to provide a final answer to the user, respond with:
<THINK>
Your reasoning about the final answer.
</THINK>
<ANSWER>
Your final answer here, formatted in Markdown.
</ANSWER>

Rules:
- NEVER ask the user to run commands for you. Run them yourself using the <EXECUTE> tag.
- ONLY output exactly one <EXECUTE> block OR one <ANSWER> block per response. Never both.
- Always wrap your thought process in <THINK> tags.
- Wait for the user or the system to provide the output of your executed command before proceeding.
- The environment is a standard bash shell.
"""

class ReActAgent:
    def __init__(self, model="llama3"):
        self.client = OllamaClient(model=model)
        self.executor = CommandExecutor()
        self.messages = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]

    def add_user_message(self, message):
        self.messages.append({"role": "user", "content": message})

    def run_turn(self):
        """Runs a single iteration of the ReAct loop."""
        response_text = self.client.chat(self.messages)
        self.messages.append({"role": "assistant", "content": response_text})

        # Parse output
        think_match = re.search(r'<THINK>(.*?)</THINK>', response_text, re.DOTALL)
        execute_match = re.search(r'<EXECUTE>(.*?)</EXECUTE>', response_text, re.DOTALL)
        answer_match = re.search(r'<ANSWER>(.*?)</ANSWER>', response_text, re.DOTALL)

        if think_match:
            console.print(Panel(think_match.group(1).strip(), title="Agent Thinking", border_style="dim yellow"))

        if execute_match:
            command = execute_match.group(1).strip()
            console.print(f"[bold cyan]Executing:[/bold cyan] {command}")

            output = self.executor.execute(command)

            console.print(Panel(output, title="Command Output", border_style="dim blue"))

            # Feed output back to agent
            self.messages.append({
                "role": "user",
                "content": f"Command Output:\n{output}\n\nWhat is your next step?"
            })
            return True # Continue loop

        elif answer_match:
            answer = answer_match.group(1).strip()
            console.print(Panel(Markdown(answer), title="Final Answer", border_style="green"))
            return False # Stop loop
        else:
            # Handle bad formatting
            console.print("[bold red]Warning:[/bold red] Agent response did not match expected format.")
            console.print(response_text)
            self.messages.append({
                "role": "user",
                "content": "Your previous response was malformed. Please ensure you use <THINK>, and either <EXECUTE> or <ANSWER> tags."
            })
            return True # Try again

    def run(self, max_steps=10):
        if not self.client.check_health():
            console.print("[bold red]Error:[/bold red] Could not connect to Ollama at http://localhost:11434")
            console.print("Please ensure Ollama is installed and running.")
            return

        style = Style.from_dict({
            'prompt': 'bold green',
        })
        session = PromptSession(style=style)

        console.print("[bold magenta]Ollama CLI Agent Started![/bold magenta] (Type 'exit' or 'quit' to stop)")

        while True:
            try:
                user_input = session.prompt('\nUser ❯ ')
                if user_input.lower() in ['exit', 'quit']:
                    break
                if not user_input.strip():
                    continue

                self.add_user_message(user_input)

                step_count = 0
                while step_count < max_steps:
                    with console.status("[bold green]Agent is thinking..."):
                        should_continue = self.run_turn()

                    if not should_continue:
                        break

                    step_count += 1

                if step_count >= max_steps:
                    console.print("[bold red]Agent reached maximum steps without finding a final answer.[/bold red]")

            except KeyboardInterrupt:
                continue
            except EOFError:
                break

if __name__ == "__main__":
    agent = ReActAgent()
    agent.run()
