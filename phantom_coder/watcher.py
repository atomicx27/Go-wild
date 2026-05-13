import os
import time
import re
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from .agent import generate_code

# Mapping of file extensions to programming languages
EXT_TO_LANG = {
    ".py": "python",
    ".js": "javascript",
    ".ts": "typescript",
    ".java": "java",
    ".cpp": "cpp",
    ".c": "c",
    ".go": "go",
    ".rs": "rust",
    ".rb": "ruby",
    ".php": "php",
    ".html": "html",
    ".css": "css",
}

class PhantomHandler(FileSystemEventHandler):
    def __init__(self):
        super().__init__()
        # Avoid processing the same file multiple times quickly
        self.last_processed = {}

    def on_modified(self, event):
        if event.is_directory:
            return

        filepath = event.src_path

        # Debounce to prevent multiple triggers for a single save
        now = time.time()
        if filepath in self.last_processed and now - self.last_processed[filepath] < 2:
            return

        self.process_file(filepath)
        self.last_processed[filepath] = now

    def on_created(self, event):
        if event.is_directory:
            return
        self.process_file(event.src_path)
        self.last_processed[event.src_path] = time.time()

    def process_file(self, filepath):
        ext = os.path.splitext(filepath)[1].lower()
        if ext not in EXT_TO_LANG:
            return

        language = EXT_TO_LANG[ext]

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except Exception as e:
            print(f"Could not read {filepath}: {e}")
            return

        modified = False
        new_lines = []

        # Pattern to match # PHANTOM:, // PHANTOM:, <!-- PHANTOM:, etc.
        phantom_pattern = re.compile(r"^\s*(#|//|<!--)\s*PHANTOM:\s*(.*)", re.IGNORECASE)

        for line in lines:
            match = phantom_pattern.match(line)
            if match:
                print(f"[Phantom] Detected request in {filepath}")
                comment_token = match.group(1)
                prompt = match.group(2).strip()
                indentation = line[:len(line) - len(line.lstrip())]

                print(f"[Phantom] Generating code for: '{prompt}'...")
                generated_code = generate_code(prompt, language)
                print(f"[Phantom] Generation complete. Applying changes.")

                # Add indentation to generated code
                indented_code = "\n".join([indentation + l for l in generated_code.split("\n")])

                new_lines.append(f"{indentation}{comment_token} Phantom generated code for: {prompt}\n")
                new_lines.append(indented_code + "\n")
                modified = True
            else:
                new_lines.append(line)

        if modified:
            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.writelines(new_lines)
                print(f"[Phantom] Successfully updated {filepath}")
            except Exception as e:
                print(f"Could not write {filepath}: {e}")

def start_watching(path="."):
    event_handler = PhantomHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    print(f"Phantom Coder is now watching '{path}' for changes...")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
