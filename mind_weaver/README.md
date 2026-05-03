# Mind Weaver

Mind Weaver is an automated, Ollama-powered Second Brain agent. It organizes raw text files dumped into an `inbox/` directory into a structured, auto-linked Zettelkasten `vault/`.

## Features
- **Auto-Categorization:** Uses LLM (via local Ollama) to classify raw notes as `code`, `journal`, or `concept`.
- **Formatting:** Automatically formats raw text into clean Markdown.
- **Action Extraction:** Identifies action items, tasks, and todos in the notes and appends them to a central `vault/KANBAN.md`.
- **Auto-Linking (Zettelkasten):** When a new `concept` is added, it is indexed in `vault/INDEX.md`. The AI then cross-references the new concept against the index to find related concepts, automatically injecting bidirectional links (`[[Concept]]`) into the Markdown files.
- **Graceful Fallback:** If Ollama is unavailable, it uses a basic mock-engine for testing purposes.

## Usage
1. Make sure Ollama is running (`http://localhost:11434`) with the `llama3` model (or adjust the script to match your model).
2. Place any raw `.txt` or `.md` notes into `mind_weaver/inbox/`.
3. Run the weaver agent:
   ```bash
   python mind_weaver/weaver.py
   ```
4. Watch as the notes are moved to `mind_weaver/vault/`, properly formatted and linked.

## Testing
Run the sample generator to populate the inbox with test data:
```bash
python mind_weaver/generate_samples.py
python mind_weaver/weaver.py
```
