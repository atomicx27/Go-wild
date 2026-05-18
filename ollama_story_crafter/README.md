# Ollama Story Crafter

An autonomous multi-agent workflow that watches an inbox for simple text prompts and writes complete, multi-chapter stories using a local Ollama instance.

## How it works

1. Drop a `.txt` file into the `ideas_inbox/` directory containing a short prompt or idea for a story.
2. The workflow will automatically pick it up and run it through a pipeline of AI agents:
    * **Director:** Reads the prompt and generates a story title, synopsis, and chapter outline.
    * **Writer:** Takes each chapter outline and drafts the chapter's content.
    * **Editor:** Reviews and polishes the drafted chapter text.
    * **Summarizer:** Reads the final chapter and creates a short summary to give context to the Writer for the next chapter.
3. Once all chapters are written and edited, the compiled story is saved as a Markdown file in the `published_stories/` directory.

## Getting Started

1. Ensure you have Ollama running locally.
2. Run `python -m ollama_story_crafter.main` (or equivalent depending on your path) to process any `.txt` files in the inbox.
