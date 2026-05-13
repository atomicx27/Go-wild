import sqlite3
import csv
import urllib.request
import json
import urllib.error
import re
import argparse
import sys

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3" # Default, could use mistral or other
VERBOSE = False

def setup_db(csv_path):
    """Loads a CSV into an in-memory SQLite database."""
    conn = sqlite3.connect(':memory:')
    cursor = conn.cursor()

    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        headers = next(reader)

        # Clean headers to be valid SQLite column names
        cleaned_headers = [re.sub(r'[^a-zA-Z0-9_]', '', h).lower() or f"col_{i}" for i, h in enumerate(headers)]

        # Create table
        cols_def = ", ".join([f"{h} TEXT" for h in cleaned_headers]) # Everything as TEXT for simplicity, could be inferred
        cursor.execute(f"CREATE TABLE data ({cols_def})")

        # Insert data
        placeholders = ", ".join(["?" for _ in cleaned_headers])
        insert_query = f"INSERT INTO data VALUES ({placeholders})"

        for row in reader:
            # Pad row if it has fewer columns than headers
            row = row + [''] * (len(cleaned_headers) - len(row))
            # Truncate if it has more
            row = row[:len(cleaned_headers)]
            cursor.execute(insert_query, row)

    conn.commit()
    return conn, cleaned_headers

def query_ollama(prompt):
    """Sends a prompt to the local Ollama instance."""
    data = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False
    }

    req = urllib.request.Request(
        OLLAMA_URL,
        data=json.dumps(data).encode('utf-8'),
        headers={'Content-Type': 'application/json'}
    )

    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            return result.get('response', '')
    except urllib.error.URLError as e:
        print(f"Error connecting to Ollama: {e}")
        print("Falling back to mock response.")
        return "MOCK_RESPONSE: The Ollama server is not running or accessible."


def run_agent(conn, headers, user_query):
    """Runs a ReAct loop to answer the user query."""
    schema = ", ".join(headers)

    system_prompt = f"""You are a Data Analyst Agent. You have access to an SQLite database with one table called 'data'.
The columns in the 'data' table are: {schema}

To answer the user's question, you must follow this exact format for your responses:
Thought: <your reasoning about what to do next>
Action: <either "ExecuteSQL" or "FinalAnswer">
Action Input: <the SQL query to run, OR the final answer to the user>

Examples:
Thought: I need to see how many rows are in the table.
Action: ExecuteSQL
Action Input: SELECT COUNT(*) FROM data;

Thought: I have the result. The count is 50.
Action: FinalAnswer
Action Input: The table has 50 rows.

Only use standard SQLite syntax. Always think first, then act.
User Question: {user_query}
"""

    history = system_prompt
    max_steps = 10

    for step in range(max_steps):
        if VERBOSE:
            print(f"\n--- Step {step + 1} ---")

        response = query_ollama(history)

        if VERBOSE:
            print(f"Agent:\n{response}")

        history += f"\n\n{response}\n"

        # Parse the response
        # Look for Action and Action Input
        action_match = re.search(r'Action:\s*(.*)', response, re.IGNORECASE)
        action_input_match = re.search(r'Action Input:\s*(.*)', response, re.IGNORECASE | re.DOTALL)

        if not action_match or not action_input_match:
            # Try to handle malformed output by asking it to correct itself
            error_msg = "Observation: Error - Could not find 'Action:' or 'Action Input:' in your response. Please follow the required format."
            history += f"{error_msg}\n"
            if VERBOSE:
                print(error_msg)
            continue

        action = action_match.group(1).strip()
        action_input = action_input_match.group(1).strip().strip("`") # Remove markdown formatting if any

        if "FinalAnswer" in action:
            return action_input

        elif "ExecuteSQL" in action:
            if VERBOSE:
                print(f"\nExecuting SQL: {action_input}")
            try:
                cursor = conn.cursor()
                cursor.execute(action_input)
                results = cursor.fetchall()
                # Format results for the prompt
                result_str = "Observation: " + str(results)
            except Exception as e:
                result_str = f"Observation: SQL Error - {e}"

            if VERBOSE:
                print(result_str)

            history += f"\n{result_str}\n"
        else:
            history += f"\nObservation: Unknown action '{action}'. Use ExecuteSQL or FinalAnswer.\n"

    return "Agent failed to find an answer within the maximum number of steps."


def main():
    parser = argparse.ArgumentParser(description="Autonomous Data Analyst Agent")
    parser.add_argument("csv_file", help="Path to the CSV file to analyze")
    parser.add_argument("query", help="The question you want to ask about the data")
    parser.add_argument("--model", default="llama3", help="Ollama model to use")
    parser.add_argument("-v", "--verbose", action="store_true", help="Show agent's reasoning steps")

    args = parser.parse_args()

    global MODEL_NAME, VERBOSE
    MODEL_NAME = args.model
    VERBOSE = args.verbose

    print(f"Loading {args.csv_file} into memory...")
    try:
        conn, headers = setup_db(args.csv_file)
        print(f"Successfully loaded. Detected columns: {', '.join(headers)}")
    except Exception as e:
        print(f"Error loading CSV: {e}")
        sys.exit(1)

    print(f"\nAsking Agent: '{args.query}'\n")
    print("Agent is thinking...\n")

    final_answer = run_agent(conn, headers, args.query)

    print("\n================ FINAL ANSWER ================\n")
    print(final_answer)
    print("\n==============================================\n")

if __name__ == "__main__":
    main()
