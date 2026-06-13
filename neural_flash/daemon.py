import os
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from agent import process_file
from models import init_db

class InboxHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory:
            # Wait a brief moment to ensure file is completely written
            time.sleep(0.5)
            process_file(event.src_path)

if __name__ == "__main__":
    init_db()

    inbox_dir = os.path.join(os.path.dirname(__file__), 'inbox')
    os.makedirs(inbox_dir, exist_ok=True)

    event_handler = InboxHandler()
    observer = Observer()
    observer.schedule(event_handler, inbox_dir, recursive=False)

    print(f"Starting daemon, watching {inbox_dir}...")
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
