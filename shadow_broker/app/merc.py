import time
import requests
import json
from .database import SessionLocal, Bounty

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "qwen2.5:0.5b"

def ask_ollama(prompt):
    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False
    }
    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=30)
        response.raise_for_status()
        return response.json().get('response', '').strip()
    except Exception as e:
        print(f"[Mercenary] Ollama error: {e}")
        return None

def process_bounties():
    db = SessionLocal()
    bounties = db.query(Bounty).filter_by(status='OPEN').all()

    for bounty in bounties:
        print(f"[Mercenary] Claiming bounty ID {bounty.id} in {bounty.filepath}...")

        # Mark as CLAIMED so it isn't picked up twice
        bounty.status = 'CLAIMED'
        db.commit()

        prompt = f"""
You are an elite code mercenary. You must fix the following code snippet based on the {bounty.comment_type} comment.

Task: {bounty.description}

Original Code:
{bounty.original_code}

Provide ONLY the corrected Python code snippet. No explanations, no markdown formatting (do not use ```python), just the raw text of the fixed code.
"""

        fix = ask_ollama(prompt)
        if fix:
            print(f"[Mercenary] Generated fix for bounty ID {bounty.id}")
            bounty.proposed_fix = fix
            bounty.status = 'COMPLETED'
        else:
            print(f"[Mercenary] Failed to generate fix for bounty ID {bounty.id}")
            bounty.status = 'OPEN' # Release claim

        db.commit()

    db.close()

def run_merc_loop():
    while True:
        try:
            process_bounties()
        except Exception as e:
            print(f"[Mercenary] Error: {e}")
        time.sleep(20) # Poll every 20 seconds

if __name__ == "__main__":
    process_bounties()
