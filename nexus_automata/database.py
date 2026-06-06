import sqlite3
import json
from pathlib import Path

DB_FILE = "nexus.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS workflows (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            goal TEXT NOT NULL,
            steps_json TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            workflow_id INTEGER,
            status TEXT DEFAULT 'running',
            logs TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (workflow_id) REFERENCES workflows(id)
        )
    ''')
    conn.commit()
    conn.close()

def save_workflow(goal: str, steps: list) -> int:
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO workflows (goal, steps_json) VALUES (?, ?)",
        (goal, json.dumps(steps))
    )
    workflow_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return workflow_id

def get_workflows():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM workflows ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_workflow(workflow_id: int):
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM workflows WHERE id = ?", (workflow_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def create_run(workflow_id: int) -> int:
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO runs (workflow_id) VALUES (?)", (workflow_id,))
    run_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return run_id

def update_run_logs(run_id: int, log_entry: str, status: str = None):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Append log
    cursor.execute("SELECT logs FROM runs WHERE id = ?", (run_id,))
    row = cursor.fetchone()
    current_logs = row[0] if row else ""
    new_logs = current_logs + log_entry + "\n"

    if status:
        cursor.execute("UPDATE runs SET logs = ?, status = ? WHERE id = ?", (new_logs, status, run_id))
    else:
        cursor.execute("UPDATE runs SET logs = ? WHERE id = ?", (new_logs, run_id))

    conn.commit()
    conn.close()

def get_run_logs(run_id: int):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT logs, status FROM runs WHERE id = ?", (run_id,))
    row = cursor.fetchone()
    conn.close()
    return {"logs": row[0], "status": row[1]} if row else {"logs": "", "status": "not_found"}
