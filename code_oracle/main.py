import os
import sys

# Ensure the parent directory is in path for module imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from code_oracle import indexer
from code_oracle import server

def main():
    print("="*50)
    print("       CODE ORACLE - Local RAG Engine")
    print("="*50)

    db_path = os.path.join(os.path.dirname(__file__), "code_index.db")

    # Check if we need to build the index
    if not os.path.exists(db_path):
        print("[System] No index found. Building index...")
        # Since we run from root usually, we index the parent directory
        indexer.index_codebase(".")
    else:
        print("[System] Existing index found. To rebuild, delete 'code_oracle/code_index.db'.")

    print("-" * 50)
    # Start server
    server.run_server()

if __name__ == "__main__":
    main()
