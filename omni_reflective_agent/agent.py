import os
import json
import time
import urllib.request
import urllib.error
import logging
from pathlib import Path

# Setup basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

OLLAMA_API_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "qwen2.5:0.5b"

def ensure_directories():
    """Ensure dynamic I/O directories exist."""
    dirs = ['inbox', 'processed', 'outbox', 'rejected']
    for d in dirs:
        os.makedirs(d, exist_ok=True)
    return dirs

def call_ollama(prompt):
    """Call local Ollama using standard library."""
    data = json.dumps({
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False
    }).encode('utf-8')

    req = urllib.request.Request(OLLAMA_API_URL, data=data, headers={'Content-Type': 'application/json'})

    try:
        with urllib.request.urlopen(req, timeout=60) as response:
            result = json.loads(response.read().decode('utf-8'))
            return result.get("response", "").strip()
    except Exception as e:
        logging.error(f"Error calling Ollama: {e}")
        return None

def process_file(file_path):
    """Reflective multi-step workflow."""
    with open(file_path, 'r') as f:
        topic = f.read().strip()

    if not topic:
        logging.warning(f"File {file_path} is empty. Rejecting.")
        return False

    logging.info(f"Processing topic: {topic}")

    # Step 1: Draft
    logging.info("Generating draft...")
    draft_prompt = f"Write a short, creative paragraph about: {topic}"
    draft = call_ollama(draft_prompt)
    if not draft: return False

    # Step 2: Critique
    logging.info("Critiquing draft...")
    critique_prompt = f"Critique the following text and suggest one specific improvement:\n\n{draft}"
    critique = call_ollama(critique_prompt)
    if not critique: return False

    # Step 3: Revise
    logging.info("Revising based on critique...")
    revise_prompt = f"Revise the following text based on this critique:\n\nText: {draft}\n\nCritique: {critique}"
    revision = call_ollama(revise_prompt)
    if not revision: return False

    # Save output
    base_name = os.path.basename(file_path)
    out_path = os.path.join('outbox', f"result_{base_name}")
    with open(out_path, 'w') as f:
        f.write(f"--- TOPIC ---\n{topic}\n\n")
        f.write(f"--- DRAFT ---\n{draft}\n\n")
        f.write(f"--- CRITIQUE ---\n{critique}\n\n")
        f.write(f"--- REVISION ---\n{revision}\n")

    logging.info(f"Successfully processed and saved to {out_path}")
    return True

def run_agent_loop():
    """Main autonomous loop watching the inbox."""
    ensure_directories()
    logging.info("Agent started. Watching 'inbox/' directory...")

    while True:
        # Check inbox
        inbox_files = [f for f in os.listdir('inbox') if f.endswith('.txt')]

        for file_name in inbox_files:
            file_path = os.path.join('inbox', file_name)

            success = process_file(file_path)

            if success:
                os.rename(file_path, os.path.join('processed', file_name))
            else:
                os.rename(file_path, os.path.join('rejected', file_name))

        time.sleep(2)  # Wait before polling again

if __name__ == "__main__":
    run_agent_loop()
