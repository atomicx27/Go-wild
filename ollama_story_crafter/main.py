import os
import time
from .client import OllamaClient
from .agents import director_agent, writer_agent, editor_agent, summarizer_agent

import re

INBOX_DIR = os.path.join(os.path.dirname(__file__), "ideas_inbox")
OUTBOX_DIR = os.path.join(os.path.dirname(__file__), "published_stories")

def process_prompt_file(filepath: str, client: OllamaClient):
    filename = os.path.basename(filepath)
    print(f"\n--- Processing new idea: {filename} ---")

    with open(filepath, 'r', encoding='utf-8') as f:
        prompt = f.read().strip()

    if not prompt:
        print(f"Skipping {filename}: file is empty.")
        os.remove(filepath)
        return

    # Phase 1: Director creates outline
    outline = director_agent(client, prompt)
    if not outline or 'title' not in outline:
        print("Failed to generate outline. Skipping.")
        return

    title = outline.get('title', 'Untitled Story')
    synopsis = outline.get('synopsis', '')
    chapters_info = outline.get('chapters', [])

    print(f"Story Title: {title}")
    print(f"Synopsis: {synopsis}")
    print(f"Chapters to write: {len(chapters_info)}")

    story_content = f"# {title}\n\n**Synopsis:** {synopsis}\n\n---\n\n"
    previous_chapters_summary = ""

    # Phase 2 & 3: Writer and Editor for each chapter
    for chapter_info in chapters_info:
        # Write
        raw_chapter = writer_agent(client, synopsis, chapter_info, previous_chapters_summary)

        # Edit
        edited_chapter = editor_agent(client, raw_chapter)

        # Summarize for context
        chapter_summary = summarizer_agent(client, edited_chapter)
        previous_chapters_summary += f"Chapter {chapter_info['chapter_number']}: {chapter_summary}\n"

        # Append to main story
        story_content += f"## Chapter {chapter_info['chapter_number']}: {chapter_info['title']}\n\n"
        story_content += edited_chapter + "\n\n---\n\n"

    # Phase 4: Publish
    # Strip any dangerous characters from title to prevent path traversal
    safe_title = re.sub(r'[^a-zA-Z0-9_\-]', '', title.replace(' ', '_')).lower()
    output_filename = f"{safe_title}.md"
    output_path = os.path.join(OUTBOX_DIR, output_filename)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(story_content)

    print(f"Story successfully published to: {output_path}")

    # Cleanup inbox
    os.remove(filepath)
    print(f"Removed processed file: {filepath}")

def main():
    os.makedirs(INBOX_DIR, exist_ok=True)
    os.makedirs(OUTBOX_DIR, exist_ok=True)

    print(f"Ollama Story Crafter initialized.")
    print(f"Watching {INBOX_DIR} for new idea prompts...")

    client = OllamaClient()

    # Run once to process existing files then exit for testing simplicity,
    # but could be wrapped in a while True loop for continuous watching.
    for filename in os.listdir(INBOX_DIR):
        if filename.endswith(".txt"):
            filepath = os.path.join(INBOX_DIR, filename)
            process_prompt_file(filepath, client)

if __name__ == "__main__":
    main()
