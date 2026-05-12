# Phantom Coder

An autonomous background daemon that watches your codebase and writes code for you in real-time, powered by a local Ollama instance.

## Concept
Instead of context-switching to ChatGPT or another AI tool, you simply write a comment in your source file requesting what you want, save the file, and `Phantom Coder` instantly generates the code and injects it right back into your editor.

## Prerequisites
- **Ollama**: Must be installed and running locally (`http://localhost:11434`).
- **Python 3.8+**

## Installation
1. Navigate to the project directory:
   ```bash
   cd phantom_coder
   ```
2. Create a virtual environment and install dependencies:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

## Usage
Start the daemon, pointing it to the directory you want to watch (defaults to `.`):

```bash
python run.py /path/to/your/project
```

Then, in any supported source code file (`.py`, `.js`, `.ts`, `.java`, `.cpp`, etc.), write a comment starting with `PHANTOM:`:

```python
# PHANTOM: Write a function to check if a string is a valid email address
```

When you save the file, Phantom Coder will detect the change, ping your local Ollama model, and rewrite your file to include the implementation.

```python
# Phantom generated code for: Write a function to check if a string is a valid email address
import re
def is_valid_email(email):
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return re.match(pattern, email) is not None
```
