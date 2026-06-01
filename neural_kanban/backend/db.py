import sqlite3
import os
import json
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'kanban.db')

def get_connection():
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tickets (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            description TEXT,
            status TEXT NOT NULL,
            ai_processed BOOLEAN NOT NULL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticket_id TEXT NOT NULL,
            author TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (ticket_id) REFERENCES tickets(id)
        )
    ''')

    conn.commit()
    conn.close()

def add_ticket(ticket_id: str, title: str, description: str, status: str = 'TODO'):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO tickets (id, title, description, status, ai_processed) VALUES (?, ?, ?, ?, 0)',
        (ticket_id, title, description, status)
    )
    conn.commit()
    conn.close()

def get_tickets():
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM tickets ORDER BY created_at DESC')
    tickets = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return tickets

def get_ticket(ticket_id: str):
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM tickets WHERE id = ?', (ticket_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def update_ticket_status(ticket_id: str, status: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE tickets SET status = ? WHERE id = ?', (status, ticket_id))
    conn.commit()
    conn.close()

def mark_ticket_processed(ticket_id: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE tickets SET ai_processed = 1 WHERE id = ?', (ticket_id,))
    conn.commit()
    conn.close()

def add_comment(ticket_id: str, author: str, content: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO comments (ticket_id, author, content) VALUES (?, ?, ?)',
        (ticket_id, author, content)
    )
    conn.commit()
    conn.close()

def get_comments(ticket_id: str):
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM comments WHERE ticket_id = ? ORDER BY created_at ASC', (ticket_id,))
    comments = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return comments

def get_unprocessed_tickets():
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM tickets WHERE ai_processed = 0')
    tickets = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return tickets
