import os
import time
import shutil
import csv
from pathlib import Path
from agents import DataAnalyst, FrontendEngineer, QAChecker

INBOX_DIR = "inbox"
OUTBOX_DIR = "outbox"
PROCESSED_DIR = "processed"

def setup_dirs():
    for d in [INBOX_DIR, OUTBOX_DIR, PROCESSED_DIR]:
        Path(d).mkdir(exist_ok=True)

def process_csv(filepath: Path):
    print(f"\n--- Processing {filepath.name} ---")

    # 1. Read entire CSV and get a sample
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        columns = next(reader, [])
        sample_rows = [columns] + [next(reader, []) for _ in range(5)]

    sample_csv = "\n".join([",".join(row) for row in sample_rows])

    # Initialize agents
    analyst = DataAnalyst()
    engineer = FrontendEngineer()
    qa = QAChecker()

    # 2. Analyst creates plan
    print("[1/4] Analyst is examining data and planning visualizations...")
    analysis_plan = analyst.analyze(sample_csv)
    if "error" in analysis_plan:
        print(f"Error from Analyst: {analysis_plan['error']}. Aborting.")
        return

    print(f"Analyst plan: {analysis_plan}")

    # 3. Engineer builds HTML + QA loop
    max_retries = 3
    final_html = ""
    for attempt in range(max_retries):
        print(f"[2/4] Engineer is building the dashboard (Attempt {attempt+1}/{max_retries})...")
        html_code = engineer.generate_dashboard(columns, analysis_plan)

        # Clean up markdown if model ignored instructions
        if html_code.startswith("```html"):
            html_code = html_code[7:]
        if html_code.endswith("```"):
            html_code = html_code[:-3]

        print("[3/4] QA is checking the generated dashboard...")
        passed, msg = qa.verify(html_code)

        if passed:
            final_html = html_code
            print("QA Passed!")
            break
        else:
            print(f"QA Failed: {msg}. Retrying...")

    if not final_html:
        print("Failed to generate valid HTML after retries. Aborting.")
        return

    # 4. Inject actual data and save
    print("[4/4] Injecting data and saving to outbox...")
    final_html = final_html.replace("__CSV_DATA__", content)

    out_filename = filepath.stem + "_dashboard.html"
    out_path = Path(OUTBOX_DIR) / out_filename
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(final_html)

    print(f"Dashboard saved to {out_path}!")

    # Move original to processed
    shutil.move(filepath, Path(PROCESSED_DIR) / filepath.name)
    print(f"Moved {filepath.name} to {PROCESSED_DIR}/")

def main():
    setup_dirs()
    print(f"Data Forge is running. Drop CSV files into data_forge/{INBOX_DIR}/ to begin...")

    try:
        while True:
            for item in Path(INBOX_DIR).glob("*.csv"):
                process_csv(item)
            time.sleep(2)
    except KeyboardInterrupt:
        print("\nShutting down Data Forge.")

if __name__ == "__main__":
    main()
