import os

WORKSPACE_DIR = os.path.join(os.path.dirname(__file__), 'workspace')

def secure_path(filepath: str) -> str:
    """Ensure the path is within the workspace directory to prevent path traversal."""
    normalized = os.path.normpath(os.path.join(WORKSPACE_DIR, filepath))
    if not normalized.startswith(WORKSPACE_DIR):
        raise ValueError(f"Access denied. Path {filepath} is outside the workspace.")
    return normalized

def read_file(filepath: str) -> str:
    """Read a file from the workspace."""
    try:
        path = secure_path(filepath)
        if not os.path.exists(path):
            return f"Error: File '{filepath}' does not exist."
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {str(e)}"

def write_file(filepath: str, content: str) -> str:
    """Write a file to the workspace."""
    try:
        path = secure_path(filepath)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"Successfully wrote to '{filepath}'."
    except Exception as e:
        return f"Error writing file: {str(e)}"

def list_files(directory: str = ".") -> str:
    """List files in the workspace directory."""
    try:
        path = secure_path(directory)
        if not os.path.exists(path) or not os.path.isdir(path):
             return f"Error: Directory '{directory}' does not exist."

        files = []
        for item in os.listdir(path):
            item_path = os.path.join(path, item)
            if os.path.isdir(item_path):
                files.append(f"{item}/")
            else:
                files.append(item)
        return "\n".join(files) if files else "Directory is empty."
    except Exception as e:
        return f"Error listing files: {str(e)}"

def python_eval(code: str) -> str:
    """Evaluate python code inside the workspace."""
    import sys
    from io import StringIO

    # Simple sandboxing effort (not secure for real untrusted code, but enough for agent)
    old_stdout = sys.stdout
    sys.stdout = StringIO()
    try:
        # Execute the code in the context of the workspace directory
        current_dir = os.getcwd()
        os.chdir(WORKSPACE_DIR)

        try:
            exec(code, {})
        finally:
            os.chdir(current_dir)

        output = sys.stdout.getvalue()
        return output if output else "Code executed successfully. No output."
    except Exception as e:
        return f"Error executing python code: {str(e)}"
    finally:
        sys.stdout = old_stdout
