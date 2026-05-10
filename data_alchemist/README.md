# Data Alchemist

An autonomous agentic workflow that reads structured data files from an `inbox`, uses Ollama to dynamically generate Python scripts to analyze or transform the data, executes the generated scripts in a safe `workspace`, and saves the results to an `outbox`. Original files are moved to an `archive`.

## Architecture
- **Inbox**: Drop data files (CSV, JSON, etc.) here.
- **Outbox**: The resulting artifacts (processed data, plots, insights) are saved here.
- **Workspace**: A temporary directory where the generated Python scripts are saved and executed.
- **Archive**: Original data files are moved here after processing.
- **Alchemist**: The main polling and agentic orchestrator script. It features an automated self-healing loop: if a generated script throws an error, it captures `stderr`, returns it to the LLM for a fix, and retries.

*Go wild and experiment!*