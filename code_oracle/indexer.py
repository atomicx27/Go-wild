import os
import sqlite3
import re
from pathlib import Path

DB_PATH = "code_oracle/code_index.db"
IGNORE_DIRS = {".git", "node_modules", "venv", "__pycache__", ".pytest_cache", "static", "code_oracle/code_index.db"}
IGNORE_EXTENSIONS = {".pyc", ".db", ".sqlite", ".sqlite3", ".log", ".png", ".jpg", ".jpeg", ".gif", ".ico", ".webm", ".mp4"}

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    c = conn.cursor()
    # Drop table if exists for a fresh index (can be optimized later)
    c.execute("DROP TABLE IF EXISTS code_index")
    # FTS5 virtual table for full-text search
    c.execute('''
        CREATE VIRTUAL TABLE code_index USING fts5(
            filepath,
            content,
            tokenize='trigram'
        )
    ''')
    conn.commit()
    conn.close()

def chunk_text(text, max_lines=50):
    lines = text.split('\n')
    chunks = []
    for i in range(0, len(lines), max_lines):
        chunk = '\n'.join(lines[i:i + max_lines])
        chunks.append(chunk)
    return chunks

def index_codebase(root_path="."):
    init_db()
    conn = get_connection()
    c = conn.cursor()

    indexed_files = 0
    indexed_chunks = 0

    print(f"Indexing codebase at {os.path.abspath(root_path)}...")

    for dirpath, dirnames, filenames in os.walk(root_path):
        # Filter out ignored directories
        dirnames[:] = [d for d in dirnames if not any(ignored in os.path.join(dirpath, d) for ignored in IGNORE_DIRS)]

        for filename in filenames:
            ext = os.path.splitext(filename)[1]
            if ext in IGNORE_EXTENSIONS:
                continue

            filepath = os.path.join(dirpath, filename)

            # Skip the db itself
            if DB_PATH in filepath:
                continue

            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
            except UnicodeDecodeError:
                continue # Skip binary or non-utf8 files
            except Exception as e:
                print(f"Error reading {filepath}: {e}")
                continue

            chunks = chunk_text(content)
            for chunk in chunks:
                c.execute(
                    "INSERT INTO code_index (filepath, content) VALUES (?, ?)",
                    (filepath, chunk)
                )
                indexed_chunks += 1
            indexed_files += 1

    conn.commit()
    conn.close()
    print(f"Indexing complete! Indexed {indexed_files} files into {indexed_chunks} chunks.")

def search_codebase(query, limit=5):
    conn = get_connection()
    c = conn.cursor()

    # Simple FTS5 MATCH query
    # Using trigram we can just match text, but let's format it for FTS
    # Enclosing in quotes helps with phrases, but we might just want to let sqlite handle it
    # We'll use a basic match. If it fails we can fallback.

    # Sanitize query for FTS5 (remove quotes that might break syntax)
    safe_query = query.replace('"', '""')

    try:
        c.execute("""
            SELECT filepath, content, rank
            FROM code_index
            WHERE code_index MATCH ?
            ORDER BY rank
            LIMIT ?
        """, (f'"{safe_query}"', limit))
        results = c.fetchall()
    except sqlite3.OperationalError as e:
        # Fallback to simple LIKE if FTS query syntax is invalid
        print(f"FTS error: {e}. Falling back to LIKE.")
        c.execute("""
            SELECT filepath, content, 0 as rank
            FROM code_index
            WHERE content LIKE ?
            LIMIT ?
        """, (f"%{query}%", limit))
        results = c.fetchall()

    conn.close()

    formatted_results = []
    for row in results:
        formatted_results.append({
            "filepath": row["filepath"],
            "content": row["content"]
        })
    return formatted_results

if __name__ == "__main__":
    index_codebase()
    # Test search
    res = search_codebase("def", limit=1)
    print(f"Found {len(res)} results for 'def'")
