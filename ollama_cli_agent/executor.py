import subprocess
import os

class CommandExecutor:
    def __init__(self, timeout=30):
        self.timeout = timeout
        self.cwd = os.getcwd()

    def execute(self, command):
        """
        Executes a shell command and returns the output.
        Handles `cd` commands explicitly to maintain state.
        """
        # Handle stateful 'cd' commands
        if command.strip().startswith("cd "):
            target_dir = command.strip().split(" ", 1)[1]
            try:
                os.chdir(target_dir)
                self.cwd = os.getcwd()
                return f"Changed directory to {self.cwd}"
            except FileNotFoundError:
                return f"Error: Directory '{target_dir}' not found."
            except Exception as e:
                return f"Error changing directory: {e}"

        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=self.cwd,
                capture_output=True,
                text=True,
                timeout=self.timeout
            )

            output = ""
            if result.stdout:
                output += result.stdout
            if result.stderr:
                output += f"\nSTDERR:\n{result.stderr}"

            if not output.strip():
                return "Command executed successfully with no output."

            # Truncate output if it's too long to avoid overflowing the context window
            MAX_LENGTH = 4000
            if len(output) > MAX_LENGTH:
                return output[:MAX_LENGTH] + f"\n...[Output truncated, exceeded {MAX_LENGTH} characters]"

            return output

        except subprocess.TimeoutExpired:
            return f"Command timed out after {self.timeout} seconds."
        except Exception as e:
            return f"Error executing command: {e}"
