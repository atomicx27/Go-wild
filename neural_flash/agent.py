import asyncio
import os
import glob
import json
import httpx
import logging
from .db import init_db, add_card, get_cards_needing_mnemonics, update_card_mnemonic

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("neural_flash_agent")

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "llama3"

INBOX_DIR = os.path.join(os.path.dirname(__file__), "inbox")
PROCESSED_DIR = os.path.join(os.path.dirname(__file__), "processed")
os.makedirs(INBOX_DIR, exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)

async def generate_cards_from_text(text):
    prompt = f"""
    Extract key information from the following text and convert it into a list of flashcards.
    Return ONLY a JSON array of objects, where each object has a 'question' and 'answer' field.
    Do not include any other text or markdown formatting.

    Text:
    {text}
    """

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                OLLAMA_URL,
                json={
                    "model": MODEL,
                    "messages": [{"role": "user", "content": prompt}],
                    "stream": False,
                    "format": "json"
                },
                timeout=60.0
            )
            response.raise_for_status()
            data = response.json()
            return json.loads(data["message"]["content"])
    except Exception as e:
        logger.error(f"Error generating cards: {e}")
        return []

async def generate_mnemonic_for_card(question, answer):
    prompt = f"""
    Create a clever, memorable mnemonic or a short, intuitive explanation to help remember this flashcard.
    Keep it concise.

    Question: {question}
    Answer: {answer}
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                OLLAMA_URL,
                json={
                    "model": MODEL,
                    "messages": [{"role": "user", "content": prompt}],
                    "stream": False
                },
                timeout=60.0
            )
            response.raise_for_status()
            data = response.json()
            return data["message"]["content"].strip()
    except Exception as e:
        logger.error(f"Error generating mnemonic: {e}")
        return None

async def process_inbox():
    while True:
        for filepath in glob.glob(os.path.join(INBOX_DIR, "*.txt")):
            logger.info(f"Processing file: {filepath}")
            try:
                with open(filepath, "r") as f:
                    content = f.read()

                cards = await generate_cards_from_text(content)
                filename = os.path.basename(filepath)

                for card in cards:
                    if "question" in card and "answer" in card:
                        add_card(card["question"], card["answer"], filename)
                        logger.info(f"Added card: {card['question']}")

                os.rename(filepath, os.path.join(PROCESSED_DIR, filename))
                logger.info(f"Moved {filename} to processed directory.")

            except Exception as e:
                logger.error(f"Failed to process {filepath}: {e}")

        await asyncio.sleep(10)

async def generate_mnemonics_loop():
    while True:
        try:
            cards = get_cards_needing_mnemonics()
            for card in cards:
                logger.info(f"Generating mnemonic for hard card ID: {card['id']}")
                mnemonic = await generate_mnemonic_for_card(card["question"], card["answer"])
                if mnemonic:
                    update_card_mnemonic(card["id"], mnemonic)
                    logger.info(f"Updated mnemonic for card ID: {card['id']}")
        except Exception as e:
             logger.error(f"Error in mnemonic loop: {e}")
        await asyncio.sleep(60)

async def main():
    init_db()
    logger.info("Starting Neural Flash Agent...")
    await asyncio.gather(
        process_inbox(),
        generate_mnemonics_loop()
    )

if __name__ == "__main__":
    asyncio.run(main())
