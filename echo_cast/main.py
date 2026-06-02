import os
import time
import shutil
from pipeline import process_file

# Setup paths relative to this script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INBOX_DIR = os.path.join(BASE_DIR, "inbox")
OUTBOX_DIR = os.path.join(BASE_DIR, "outbox")
ARCHIVE_DIR = os.path.join(BASE_DIR, "archive")

def main():
    print(f"Echo Cast Daemon Initialized.")
    print(f"Watching directory: {INBOX_DIR}")

    # Ensure directories exist (sanity check)
    for d in [INBOX_DIR, OUTBOX_DIR, ARCHIVE_DIR]:
        os.makedirs(d, exist_ok=True)

    try:
        while True:
            # Look for txt or md files
            files = [f for f in os.listdir(INBOX_DIR) if f.endswith('.txt') or f.endswith('.md')]

            for file in files:
                file_path = os.path.join(INBOX_DIR, file)
                print(f"\n--- Signal Detected: {file} ---")

                try:
                    # Process the file
                    process_file(file_path, OUTBOX_DIR)

                    # Move to archive upon success
                    archive_path = os.path.join(ARCHIVE_DIR, file)
                    shutil.move(file_path, archive_path)
                    print(f"Transmission archived: {file}")

                except Exception as e:
                    print(f"Error processing {file}: {e}")

            # Wait before checking again
            time.sleep(5)

    except KeyboardInterrupt:
        print("\nDaemon terminated by user.")

if __name__ == "__main__":
    main()
