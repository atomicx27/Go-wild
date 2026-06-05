import subprocess
import shlex

def execute_bash(command: str, timeout: int = 30) -> str:
    """
    Executes a bash command safely using subprocess and returns the output.
    """
    try:
        # Run the command with shell=True to support bash builtins like cd, ls, pipes
        # We capture both stdout and stderr
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout
        )

        output = ""
        if result.stdout:
            output += f"STDOUT:\n{result.stdout}\n"
        if result.stderr:
            output += f"STDERR:\n{result.stderr}\n"

        if result.returncode != 0:
            output += f"Exit code: {result.returncode}"

        if not output.strip():
            return "Command executed successfully with no output."

        return output.strip()
    except subprocess.TimeoutExpired:
        return f"Command timed out after {timeout} seconds."
    except Exception as e:
        return f"Error executing command: {str(e)}"
