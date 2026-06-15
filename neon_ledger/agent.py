import os
import time
import pandas as pd
import json
import httpx
import logging
import sqlite3
import shutil
from neon_ledger.database import get_connection, init_db

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

INBOX_DIR = os.path.join(os.path.dirname(__file__), 'inbox')
PROCESSED_DIR = os.path.join(os.path.dirname(__file__), 'processed')
REJECTED_DIR = os.path.join(os.path.dirname(__file__), 'rejected')

os.makedirs(INBOX_DIR, exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)
os.makedirs(REJECTED_DIR, exist_ok=True)

def process_file(filepath):
    logging.info(f"Processing file: {filepath}")
    try:
        df = pd.read_csv(filepath)
        if df.empty:
            logging.warning("CSV is empty.")
            return None

        # Ensure we have date, description, amount at least roughly
        df.columns = [c.lower().strip() for c in df.columns]

        if 'date' not in df.columns or 'amount' not in df.columns or 'description' not in df.columns:
            logging.error(f"Missing required columns (date, description, amount) in {filepath}")
            return None

        # Format dataframe to a string for the AI
        csv_string = df.to_csv(index=False)
        return csv_string, df
    except Exception as e:
        logging.error(f"Failed to process file {filepath}: {e}")
        return None

def save_results(df, analysis):
    conn = get_connection()
    cursor = conn.cursor()

    categories = analysis.get("categories", [])

    # Pad categories if Ollama didn't return enough
    if len(categories) < len(df):
        categories.extend(["Unknown"] * (len(df) - len(categories)))

    for i, row in df.iterrows():
        cat = categories[i] if i < len(categories) else "Unknown"
        cursor.execute(
            "INSERT INTO transactions (date, description, amount, category) VALUES (?, ?, ?, ?)",
            (str(row['date']), str(row['description']), float(row['amount']), str(cat))
        )

    report = analysis.get("report", "No report generated.")
    cursor.execute("INSERT INTO reports (report_text) VALUES (?)", (report,))

    conn.commit()
    conn.close()

def agent_loop():
    logging.info("Starting Neon Ledger Agent loop...")
    init_db()

    while True:
        try:
            files = [f for f in os.listdir(INBOX_DIR) if f.endswith('.csv')]
            if files:
                for file in files:
                    filepath = os.path.join(INBOX_DIR, file)
                    result = process_file(filepath)
                    filename = os.path.basename(filepath)
                    if result:
                        csv_string, df = result
                        analysis = analyze_with_ollama(csv_string)
                        if analysis:
                            save_results(df, analysis)

                            # Move to processed
                            dest = os.path.join(PROCESSED_DIR, f"{int(time.time())}_{filename}")
                            shutil.move(filepath, dest)
                            logging.info(f"Successfully processed {filename}")
                        else:
                            logging.error(f"Analysis failed for {filepath}. Moving to rejected.")
                            dest = os.path.join(REJECTED_DIR, f"{int(time.time())}_{filename}")
                            shutil.move(filepath, dest)
                    else:
                        logging.error(f"File processing failed for {filepath}. Moving to rejected.")
                        dest = os.path.join(REJECTED_DIR, f"{int(time.time())}_{filename}")
                        shutil.move(filepath, dest)
        except Exception as e:
            logging.error(f"Agent loop error: {e}")
        time.sleep(5)

def analyze_with_ollama(csv_string):
    logging.info("Requesting analysis from Ollama...")
    prompt = f"""
You are a snarky, cyberpunk AI financial advisor named 'Neon Ledger'.
Analyze the following transaction data.

Task 1: Categorize each transaction.
Task 2: Write a short, sarcastic, cyberpunk-themed financial report evaluating these spending habits.

Output exactly a JSON object with the following structure, and NO markdown or other text:
{{
    "categories": [
        "Groceries", "Entertainment", "Rent", "Tech", "Other"  // Create an array mapping to each row in the CSV (in order)
    ],
    "report": "Your snarky, cyberpunk report here in HTML format using tags like <p> and <b>."
}}

Transaction Data:
{csv_string}
"""
    try:
        response = httpx.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama3",
                "prompt": prompt,
                "stream": False,
                "format": "json"
            },
            timeout=120.0
        )
        response.raise_for_status()
        data = response.json()

        # Depending on ollama version, sometimes it wraps in response
        response_text = data.get("response", "{}")

        parsed_json = json.loads(response_text)
        return parsed_json
    except Exception as e:
        logging.error(f"Ollama request failed: {e}")
        return None
