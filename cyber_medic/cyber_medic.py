import os
import time
import json
import logging
import requests
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from jinja2 import Environment, FileSystemLoader

# Configuration
LOG_DIR = os.path.join(os.path.dirname(__file__), "logs")
REPORTS_DIR = os.path.join(os.path.dirname(__file__), "reports")
TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "templates")
OLLAMA_API_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "qwen2.5:0.5b"

# Ensure directories exist
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)
os.makedirs(TEMPLATES_DIR, exist_ok=True)

# Setup logging for the agent itself
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Global state to hold reports
incident_reports = []

class LogHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if not event.is_directory and event.src_path.endswith(".log"):
            logging.info(f"Detected modification in: {event.src_path}")
            self.process_log_file(event.src_path)

    def on_created(self, event):
        if not event.is_directory and event.src_path.endswith(".log"):
            logging.info(f"Detected new file: {event.src_path}")
            self.process_log_file(event.src_path)

    def process_log_file(self, filepath):
        try:
            with open(filepath, 'r') as f:
                content = f.read()

            # Simple heuristic: only process if it looks like an error
            if "Traceback" in content or "ERROR" in content or "Exception" in content:
                logging.info(f"Extracting error context from {os.path.basename(filepath)}...")
                diagnosis = self.diagnose_with_ollama(content)

                report = {
                    "filename": os.path.basename(filepath),
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "raw_log": content[:1000] + ("..." if len(content) > 1000 else ""), # Truncate for UI
                    "diagnosis": diagnosis.replace('\n', '<br>') # basic formatting
                }

                incident_reports.insert(0, report) # Add to top
                # Keep only last 10 reports
                if len(incident_reports) > 10:
                    incident_reports.pop()

                self.generate_dashboard()
                # To prevent re-processing the same file constantly, we might want to move it or mark it.
                # For this simple prototype, we'll just clear the file after processing.
                with open(filepath, 'w') as f:
                    f.write(f"Processed by Cyber Medic at {datetime.now().isoformat()}")

        except Exception as e:
            logging.error(f"Error processing log file {filepath}: {e}")

    def diagnose_with_ollama(self, error_content):
        prompt = f"""
        You are a highly skilled, cyberpunk-themed AI diagnostic system.
        Analyze the following error log or traceback.
        Provide a concise diagnosis of what went wrong and a clear, actionable prescription (fix) for the developer.
        Keep your response technical, direct, and under 150 words.

        ERROR LOG:
        ```
        {error_content[:1500]}
        ```

        DIAGNOSIS & PRESCRIPTION:
        """

        payload = {
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False
        }

        try:
            logging.info("Querying Ollama for diagnosis...")
            response = requests.post(OLLAMA_API_URL, json=payload, timeout=60)
            response.raise_for_status()
            result = response.json()
            return result.get("response", "Error: No response generated.")
        except requests.exceptions.RequestException as e:
            logging.error(f"Failed to communicate with Ollama: {e}")
            return f"SYSTEM FAILURE: Unable to reach diagnostic core ({MODEL_NAME}). Error: {str(e)}"

    def generate_dashboard(self):
        try:
            env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))
            template = env.get_template('report.html')

            output_html = template.render(reports=incident_reports)

            output_path = os.path.join(REPORTS_DIR, "index.html")
            with open(output_path, 'w') as f:
                f.write(output_html)

            logging.info(f"Dashboard updated at: {output_path}")
        except Exception as e:
            logging.error(f"Failed to generate dashboard: {e}")

if __name__ == "__main__":
    logging.info("Cyber Medic Agent initializing...")
    logging.info(f"Monitoring directory: {LOG_DIR}")

    # Generate initial empty dashboard
    handler = LogHandler()
    handler.generate_dashboard()

    observer = Observer()
    observer.schedule(handler, LOG_DIR, recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        logging.info("Cyber Medic Agent shutting down.")

    observer.join()
