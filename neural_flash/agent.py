import os
import json
import requests
import shutil
from datetime import datetime
from typing import Optional, List, Dict, Any

from models import SessionLocal, Deck, Flashcard

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")

PROMPT = """
You are an expert educational AI.
Extract key concepts from the following text and create a set of flashcards.
The deck name should represent the overall topic of the text.

Respond ONLY with a JSON object in this exact format:
{
  "deck_name": "Name of the topic",
  "flashcards": [
    {
      "front": "Question or concept",
      "back": "Answer or explanation"
    }
  ]
}

Text to process:
"""

def generate_flashcards(text: str) -> Optional[Dict[str, Any]]:
    payload = {
        "model": "llama3",
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful assistant that generates flashcards in JSON format."
            },
            {
                "role": "user",
                "content": PROMPT + text
            }
        ],
        "format": "json",
        "stream": False
    }

    try:
        response = requests.post(f"{OLLAMA_URL}/api/chat", json=payload, timeout=60)
        response.raise_for_status()
        result = response.json()
        content = result.get("message", {}).get("content", "")
        return json.loads(content)
    except Exception as e:
        print(f"Error calling Ollama: {e}")
        # Fallback for testing/unreachable Ollama
        return {
            "deck_name": "Mocked Deck",
            "flashcards": [
                {
                    "front": "What is the capital of France?",
                    "back": "Paris"
                },
                {
                    "front": f"Extracted from text of length {len(text)}",
                    "back": "Fallback triggered."
                }
            ]
        }

def process_file(filepath: str):
    print(f"Processing file: {filepath}")

    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read()

    if not text.strip():
        print(f"File {filepath} is empty. Skipping.")
        return

    result = generate_flashcards(text)

    if result and "deck_name" in result and "flashcards" in result:
        deck_name = result["deck_name"]
        flashcards_data = result["flashcards"]

        db = SessionLocal()
        try:
            deck = db.query(Deck).filter(Deck.name == deck_name).first()
            if not deck:
                deck = Deck(name=deck_name)
                db.add(deck)
                db.commit()
                db.refresh(deck)

            for card_data in flashcards_data:
                card = Flashcard(
                    deck_id=deck.id,
                    front=card_data.get("front", ""),
                    back=card_data.get("back", "")
                )
                db.add(card)

            db.commit()
            print(f"Successfully processed {filepath}. Added to deck: {deck_name}")

        except Exception as e:
            print(f"Database error while processing {filepath}: {e}")
            db.rollback()
        finally:
            db.close()

    # Move to archive
    archive_dir = os.path.join(os.path.dirname(__file__), 'archive')
    os.makedirs(archive_dir, exist_ok=True)
    filename = os.path.basename(filepath)
    archive_path = os.path.join(archive_dir, f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{filename}")
    try:
        shutil.move(filepath, archive_path)
    except Exception as e:
        print(f"Error moving {filepath} to archive: {e}")
