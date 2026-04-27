# Phoenix Healer

Phoenix Healer is an experimental agentic wrapper for Python scripts. It acts as an automated debugger, attempting to run a script, catching any errors, and querying a local Ollama instance to analyze the traceback and rewrite the code to fix the issue. It will repeat this process until the script runs successfully or reaches a retry limit.

## Prerequisites

- Python 3
- An Ollama instance running locally (default: `http://localhost:11434`) with the `llama3` model (or configure your own via the source).

## Usage

Run the `phoenix.py` wrapper, passing the path to the script you want it to manage:

```bash
python phoenix_healer/phoenix.py path/to/your/script.py
```

### Configuration

You can override the Ollama API URL using the `OLLAMA_URL` environment variable:

```bash
OLLAMA_URL=http://your-ollama-server:11434 python phoenix_healer/phoenix.py example_broken.py
```

## Example

An `example_broken.py` is included. It intentionally contains a simple bug.
If you run it through Phoenix Healer, it will detect the failure, ask Ollama for a fix, overwrite `example_broken.py` with the corrected code, and successfully run it on the next attempt.
