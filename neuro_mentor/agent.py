import asyncio
import json
import logging
import os
import shutil
from pathlib import Path
import httpx

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

INBOX_DIR = Path(os.path.join(os.path.dirname(__file__), "inbox"))
PROCESSED_DIR = Path(os.path.join(os.path.dirname(__file__), "processed"))
DATA_DIR = Path(os.path.join(os.path.dirname(__file__), "data"))
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3"

SYSTEM_PROMPT = """
You are an expert AI instructional designer with a Cyberpunk persona.
Given the following raw text, analyze it and generate a JSON response with exactly this structure:
{
  "title": "A short, catchy cyberpunk-themed title for this knowledge module",
  "summary": "A 2-3 sentence summary of the key concepts",
  "persona_name": "Name of the AI tutor (e.g. 'Neon Ghost', 'Syntax Weaver')",
  "persona_greeting": "A flavorful greeting from the tutor persona",
  "flashcards": [
    {"question": "...", "answer": "..."}
  ],
  "quiz": [
    {
      "question": "...",
      "options": ["A", "B", "C", "D"],
      "correct_index": 0
    }
  ]
}
Ensure the output is ONLY valid JSON. Provide at least 3 flashcards and 3 quiz questions.
"""

async def process_file(filepath: Path):
    logger.info(f"Processing new file: {filepath.name}")
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        payload = {
            "model": MODEL_NAME,
            "prompt": f"{SYSTEM_PROMPT}\n\nRAW TEXT:\n{content}",
            "stream": False,
            "format": "json"
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(OLLAMA_URL, json=payload, timeout=60.0)
                response.raise_for_status()
                result = response.json()

                # Try to parse the nested JSON
                output_text = result.get("response", "")
                parsed_data = json.loads(output_text)

                # Add an ID to the module
                module_id = filepath.stem
                parsed_data["id"] = module_id

                data_path = DATA_DIR / f"{module_id}.json"
                with open(data_path, "w", encoding="utf-8") as f:
                    json.dump(parsed_data, f, indent=2)

                logger.info(f"Successfully generated module: {module_id}")

            except Exception as e:
                logger.error(f"Error calling Ollama or parsing JSON: {e}")
                return

        # Move to processed
        shutil.move(str(filepath), str(PROCESSED_DIR / filepath.name))
        logger.info(f"Moved {filepath.name} to processed.")

    except Exception as e:
        logger.error(f"Error reading file {filepath.name}: {e}")

async def run_agent_loop():
    logger.info("Neuro-Mentor Agent started. Watching inbox...")
    while True:
        try:
            if not INBOX_DIR.exists():
                INBOX_DIR.mkdir(parents=True, exist_ok=True)
            if not PROCESSED_DIR.exists():
                PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
            if not DATA_DIR.exists():
                DATA_DIR.mkdir(parents=True, exist_ok=True)

            for filepath in INBOX_DIR.glob("*.txt"):
                await process_file(filepath)

        except Exception as e:
            logger.error(f"Agent loop error: {e}")

        await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(run_agent_loop())
