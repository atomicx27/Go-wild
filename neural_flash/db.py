import sqlite3
import os
import json

DB_FILE = os.path.join(os.path.dirname(__file__), "flashcards.db")

def get_connection():
    return sqlite3.connect(DB_FILE)

def init_db():
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS cards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT NOT NULL,
            answer TEXT NOT NULL,
            source_file TEXT,
            repetition INTEGER DEFAULT 0,
            interval INTEGER DEFAULT 0,
            ease_factor REAL DEFAULT 2.5,
            next_review REAL DEFAULT 0,
            mnemonic TEXT
        )
    ''')
    conn.commit()
    conn.close()

def add_card(question, answer, source_file):
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "INSERT INTO cards (question, answer, source_file) VALUES (?, ?, ?)",
        (question, answer, source_file)
    )
    conn.commit()
    conn.close()

def get_due_cards(current_time):
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM cards WHERE next_review <= ?", (current_time,))
    rows = c.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_all_cards():
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM cards")
    rows = c.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_card(card_id):
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM cards WHERE id = ?", (card_id,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None

def update_card_review(card_id, repetition, interval, ease_factor, next_review):
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        UPDATE cards
        SET repetition = ?, interval = ?, ease_factor = ?, next_review = ?
        WHERE id = ?
    ''', (repetition, interval, ease_factor, next_review, card_id))
    conn.commit()
    conn.close()

def update_card_mnemonic(card_id, mnemonic):
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE cards SET mnemonic = ? WHERE id = ?", (mnemonic, card_id))
    conn.commit()
    conn.close()

def get_cards_needing_mnemonics():
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM cards WHERE ease_factor < 1.7 AND (mnemonic IS NULL OR mnemonic = '')")
    rows = c.fetchall()
    conn.close()
    return [dict(row) for row in rows]

if __name__ == "__main__":
    init_db()
