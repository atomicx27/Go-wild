import os
import sqlite3
import time
import json
import threading
import urllib.request
import urllib.error
import urllib.parse
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434/api/generate")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3.1")

DB_PATH = "nexus.db"
INBOX_DIR = Path("inbox")
PROCESSED_DIR = Path("processed")
WORKSPACE_DIR = Path("workspace")

def setup_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            spec_file TEXT,
            filepath TEXT,
            description TEXT,
            status TEXT DEFAULT 'TODO',
            code TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def query_ollama(prompt, system_prompt="You are a helpful coding assistant.", format="json"):
    data = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "system": system_prompt,
        "stream": False
    }
    if format == "json":
        data["format"] = "json"

    req = urllib.request.Request(OLLAMA_URL, data=json.dumps(data).encode("utf-8"), headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode("utf-8"))
            return result.get("response", "")
    except urllib.error.URLError as e:
        print(f"Error querying Ollama: {e}")
        return ""

def architect_agent():
    print("[Architect] Starting architect agent...")
    while True:
        try:
            for filepath in INBOX_DIR.glob("*.txt"):
                print(f"[Architect] Processing {filepath.name}...")
                with open(filepath, "r") as f:
                    spec_content = f.read()

                prompt = f"""
                Break down the following software specification into a list of files that need to be created.
                For each file, provide the filepath and a detailed description of what it should contain.

                Specification:
                {spec_content}

                Respond ONLY with a JSON array of objects.
                Each object must have exactly two keys: "filepath" (string) and "description" (string).
                """

                system_prompt = "You are a software architect. Break down specs into files."
                response_text = query_ollama(prompt, system_prompt, format="json")

                if not response_text:
                    print(f"[Architect] Failed to get response from Ollama for {filepath.name}")
                    time.sleep(5)
                    continue

                try:
                    files_to_create = json.loads(response_text)
                    if not isinstance(files_to_create, list):
                        raise ValueError("Ollama response is not a list")
                except (json.JSONDecodeError, ValueError) as e:
                    print(f"[Architect] Failed to parse Ollama response as JSON array for {filepath.name}: {e}")
                    print(f"[Architect] Raw response: {response_text}")
                    time.sleep(5)
                    continue

                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                for file_info in files_to_create:
                    fpath = file_info.get("filepath")
                    desc = file_info.get("description")
                    if fpath and desc:
                        cursor.execute(
                            "INSERT INTO tasks (spec_file, filepath, description, status) VALUES (?, ?, ?, 'TODO')",
                            (filepath.name, fpath, desc)
                        )
                conn.commit()
                conn.close()

                # Move to processed
                new_path = PROCESSED_DIR / filepath.name
                filepath.rename(new_path)
                print(f"[Architect] Finished processing {filepath.name}, moved to processed/.")

        except Exception as e:
            print(f"[Architect] Error in architect agent loop: {e}")

        time.sleep(5)

def worker_agent(worker_id):
    print(f"[Worker-{worker_id}] Starting worker agent...")
    while True:
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()

            # Find a TODO task
            cursor.execute("SELECT id, filepath, description FROM tasks WHERE status = 'TODO' ORDER BY id ASC LIMIT 1")
            task = cursor.fetchone()

            if not task:
                conn.close()
                time.sleep(5)
                continue

            task_id, fpath, desc = task

            # Mark IN_PROGRESS
            cursor.execute("UPDATE tasks SET status = 'IN_PROGRESS' WHERE id = ?", (task_id,))
            conn.commit()
            conn.close()

            print(f"[Worker-{worker_id}] Writing code for {fpath}...")

            prompt = f"""
            Write the code for the following file.

            Filepath: {fpath}
            Description:
            {desc}

            Respond ONLY with the raw code. Do NOT wrap it in markdown code blocks (e.g., no ```python or ```).
            Do not include any explanations or conversational text. Just the code.
            """

            # Use format=None because we want raw text, not JSON
            code = query_ollama(prompt, system_prompt="You are an expert software developer. Write code exactly as requested.", format=None)

            # Clean up potential markdown formatting anyway just in case
            if code.startswith("```"):
                lines = code.split("\n")
                if lines[0].startswith("```"):
                    lines = lines[1:]
                if lines[-1].strip() == "```":
                    lines = lines[:-1]
                code = "\n".join(lines)

            # Save the file
            full_path = WORKSPACE_DIR / fpath
            full_path.parent.mkdir(parents=True, exist_ok=True)
            with open(full_path, "w") as f:
                f.write(code)

            # Mark DONE and save code in DB for UI
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("UPDATE tasks SET status = 'DONE', code = ? WHERE id = ?", (code, task_id))
            conn.commit()
            conn.close()

            print(f"[Worker-{worker_id}] Finished writing {fpath}.")

        except Exception as e:
            print(f"[Worker-{worker_id}] Error in worker loop: {e}")
            time.sleep(5)

class APIHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/api/tasks':
            try:
                conn = sqlite3.connect(DB_PATH)
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("SELECT id, spec_file, filepath, description, status FROM tasks ORDER BY id DESC")
                rows = cursor.fetchall()
                conn.close()

                tasks = [dict(row) for row in rows]

                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(tasks).encode('utf-8'))
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(str(e).encode('utf-8'))
        else:
            # Serve static files from the web directory
            if self.path == '/':
                self.path = '/web/index.html'
            elif not self.path.startswith('/web/'):
                self.path = '/web' + self.path

            # Translate path relative to the script directory
            # but we are running in nexus_forge so it should just work if we run from there
            return super().do_GET()

def start_web_server(port=8080):
    # Change to nexus_forge directory if not already there so 'web/' resolves correctly
    # Assumes we run `python main.py` from within nexus_forge
    print(f"[Server] Starting web UI on port {port}...")
    server_address = ('', port)
    httpd = HTTPServer(server_address, APIHandler)
    httpd.serve_forever()

if __name__ == "__main__":
    print("Initializing Nexus Forge...")
    INBOX_DIR.mkdir(exist_ok=True)
    PROCESSED_DIR.mkdir(exist_ok=True)
    WORKSPACE_DIR.mkdir(exist_ok=True)
    Path("web").mkdir(exist_ok=True)

    setup_db()

    # Start Architect Thread
    threading.Thread(target=architect_agent, daemon=True).start()

    # Start 3 Worker Threads
    for i in range(1, 4):
        threading.Thread(target=worker_agent, args=(i,), daemon=True).start()

    # Start Web Server on Main Thread
    start_web_server(8080)
