# Ollama Fun Tools

A collection of creative and agentic workflows that integrate with a local Ollama instance (defaulting to `qwen2.5:0.5b`).

## 1. Code Reviewer
Located in `code_reviewer/`.

An automated code review agent that uses Ollama to provide feedback on Python code. It focuses on bugs, readability, performance, and security.

**Usage:**
```bash
python3 code_reviewer/reviewer.py <path_to_file.py>
```

## 2. Auto Fixer
Located in `auto_fixer/`.

An autonomous agent that attempts to run a given Python script. If the script fails (e.g., SyntaxError, runtime exception), it captures the error and feeds it along with the source code back to Ollama. Ollama is prompted to return fixed code, which is then written back to the file. The process repeats until the script runs successfully or reaches a max iteration limit.

**Usage:**
```bash
python3 auto_fixer/auto_fixer.py <path_to_broken_script.py>
```

## 3. Terminal Assistant
Located in `terminal_assistant/`.

An interactive, agentic terminal assistant. You can give it instructions in natural language. If it determines a bash command is needed, it generates the command and prompts you for confirmation before executing it. The output of the command is fed back into the context for continued interaction.

**Usage:**
```bash
python3 terminal_assistant/assistant.py
```
