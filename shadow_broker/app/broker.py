import os
import time
import re
from .database import SessionLocal, Bounty

TARGET_DIR = "/app/shadow_broker/target_code"

def scan_files():
    db = SessionLocal()
    print("[Broker] Scanning for bounties...")
    for root, _, files in os.walk(TARGET_DIR):
        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                with open(filepath, 'r') as f:
                    content = f.read()

                # Basic regex to find Python comments with TODO or FIXME
                matches = re.finditer(r'#\s*(TODO|FIXME):\s*(.*)', content)
                for match in matches:
                    comment_type = match.group(1)
                    description = match.group(2).strip()

                    # Check if bounty already exists
                    existing = db.query(Bounty).filter_by(filepath=filepath, description=description).first()
                    if not existing:
                        # Extract a snippet of surrounding code (approximate)
                        lines = content.split('\n')
                        start_line = content[:match.start()].count('\n')

                        # Grab a few lines around it for context
                        start_ctx = max(0, start_line - 2)
                        end_ctx = min(len(lines), start_line + 5)
                        snippet = '\n'.join(lines[start_ctx:end_ctx])

                        print(f"[Broker] Found new bounty in {filepath}: {description}")
                        new_bounty = Bounty(
                            filepath=filepath,
                            comment_type=comment_type,
                            description=description,
                            original_code=snippet,
                            status='OPEN'
                        )
                        db.add(new_bounty)
                        db.commit()
    db.close()

def run_broker_loop():
    while True:
        try:
            scan_files()
        except Exception as e:
            print(f"[Broker] Error: {e}")
        time.sleep(15) # Scan every 15 seconds

if __name__ == "__main__":
    scan_files()
