import argparse
import sys
import os

# Add the parent directory to sys.path so we can import phantom_coder if run directly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from phantom_coder.watcher import start_watching

def main():
    parser = argparse.ArgumentParser(description="Phantom Coder - Autonomous background AI coding daemon")
    parser.add_argument("path", nargs="?", default=".", help="Directory to watch (defaults to current directory)")
    args = parser.parse_args()

    # Verify that the path exists
    if not os.path.exists(args.path):
        print(f"Error: Path '{args.path}' does not exist.")
        sys.exit(1)

    print(f"Starting Phantom Coder daemon...")
    print(f"Write a comment like '# PHANTOM: create a function to fetch user data' in any source file and save it.")
    start_watching(args.path)

if __name__ == "__main__":
    main()
