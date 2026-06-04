import os
import json
import time
import re
import urllib.request
import urllib.error

INBOX_DIR = "inbox"
HOLODECKS_DIR = "holodecks"
TEMPLATE_PATH = "templates/template.html"
OLLAMA_URL = "http://localhost:11434/api/chat"

SYSTEM_PROMPT = """You are a master game designer for a cyberpunk text adventure engine.
You will be given a theme or prompt.
You must generate a complete, valid JSON object representing the game scenario based on that theme.
Do NOT wrap the JSON in markdown blocks (like ```json), just output the raw JSON object.
Ensure the JSON exactly follows this schema:

{
  "title": "String - Game Title",
  "description": "String - Short intro description",
  "starting_room": "String - ID of the first room",
  "rooms": [
    {
      "id": "String - Unique room identifier (e.g., 'start_room')",
      "name": "String - Display name of the room",
      "description": "String - Detailed description",
      "items": [
        {
          "id": "String - Unique item ID",
          "name": "String - Display name",
          "description": "String - Item description",
          "takeable": true
        }
      ],
      "exits": {
        "north": "String - Target room ID",
        "south": {
          "target_room": "String - Target room ID",
          "locked": true,
          "required_item": "String - ID of item needed to unlock",
          "lock_message": "String - Message when trying to enter without item"
        }
      }
    }
  ],
  "all_items": [
    {
      "id": "String - Must match item IDs in rooms",
      "name": "String - Display name",
      "description": "String - Full description"
    }
  ],
  "win_condition": {
    "type": "reach_room | have_item",
    "target": "String - Room ID or Item ID",
    "message": "String - Victory message"
  }
}
"""

def prompt_ollama(messages):
    data = {
        "model": "llama3",
        "messages": messages,
        "stream": False
    }
    req = urllib.request.Request(OLLAMA_URL, data=json.dumps(data).encode('utf-8'), headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            return result['message']['content']
    except Exception as e:
        print(f"Error calling Ollama: {e}")
        return None

def watch_inbox():
    print(f"Watching {INBOX_DIR} for new scenario prompts...")
    processed_files = set()

    while True:
        try:
            current_files = set(f for f in os.listdir(INBOX_DIR) if f.endswith('.txt'))
            new_files = current_files - processed_files

            for file in new_files:
                print(f"Detected new prompt: {file}")
                process_prompt(file)
                processed_files.add(file)

        except Exception as e:
            print(f"Error in watcher loop: {e}")

        time.sleep(2)

def validate_scenario(scenario):
    errors = []

    if not isinstance(scenario, dict):
        return False, ["Root must be a JSON object."]

    required_keys = ['title', 'starting_room', 'rooms']
    for k in required_keys:
        if k not in scenario:
            errors.append(f"Missing required key: '{k}'")

    if 'rooms' in scenario:
        if not isinstance(scenario['rooms'], list) or len(scenario['rooms']) == 0:
            errors.append("'rooms' must be a non-empty list.")
        else:
            room_ids = set()
            for i, room in enumerate(scenario['rooms']):
                if 'id' not in room:
                    errors.append(f"Room at index {i} missing 'id'.")
                else:
                    room_ids.add(room['id'])

            if 'starting_room' in scenario and scenario['starting_room'] not in room_ids:
                errors.append(f"Starting room '{scenario['starting_room']}' does not exist in rooms.")

            for room in scenario['rooms']:
                if 'exits' in room:
                    for direction, exit_data in room['exits'].items():
                        target = exit_data
                        if isinstance(exit_data, dict):
                            if 'target_room' not in exit_data:
                                errors.append(f"Exit '{direction}' in room '{room.get('id')}' missing 'target_room'.")
                            else:
                                target = exit_data['target_room']
                        if target not in room_ids:
                            errors.append(f"Exit '{direction}' in room '{room.get('id')}' points to non-existent room '{target}'.")

    return len(errors) == 0, errors

def clean_json_response(raw_text):
    # Often LLMs wrap JSON in markdown even if told not to
    match = re.search(r'```(?:json)?(.*?)```', raw_text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return raw_text.strip()

def process_prompt(filename):
    filepath = os.path.join(INBOX_DIR, filename)
    with open(filepath, 'r') as f:
        prompt_text = f.read().strip()

    if not prompt_text:
        print(f"Skipping empty file: {filename}")
        return

    print(f"Generating scenario for: {prompt_text[:50]}...")

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"Create a text adventure scenario about: {prompt_text}"}
    ]

    max_retries = 3
    scenario_json = None

    for attempt in range(max_retries):
        print(f"Attempt {attempt + 1}/{max_retries} to generate valid JSON...")
        response_text = prompt_ollama(messages)

        if not response_text:
            print("Failed to get response from Ollama. Make sure it is running on localhost:11434.")
            return

        clean_text = clean_json_response(response_text)

        try:
            parsed_json = json.loads(clean_text)
            is_valid, errors = validate_scenario(parsed_json)

            if is_valid:
                scenario_json = parsed_json
                print("Successfully generated valid scenario JSON.")
                break
            else:
                error_msg = f"Generated JSON failed validation:\n" + "\n".join(errors)
                print(error_msg)
                messages.append({"role": "assistant", "content": clean_text})
                messages.append({"role": "user", "content": f"Your JSON was invalid. Please fix these errors and try again:\n{error_msg}"})
        except json.JSONDecodeError as e:
            print(f"Failed to parse JSON: {e}")
            messages.append({"role": "assistant", "content": clean_text})
            messages.append({"role": "user", "content": f"Your response was not valid JSON. Parse error: {e}. Please output ONLY valid JSON."})

    if not scenario_json:
        print(f"Failed to generate valid scenario for {filename} after {max_retries} attempts.")
        return

    # Injection
    try:
        with open(TEMPLATE_PATH, 'r') as f:
            template_content = f.read()

        # Serialize with proper escaping for embedding in script tag
        json_str = json.dumps(scenario_json)
        final_html = template_content.replace('{{SCENARIO_JSON}}', json_str)

        out_filename = filename.replace('.txt', '.html')
        out_filepath = os.path.join(HOLODECKS_DIR, out_filename)

        with open(out_filepath, 'w') as f:
            f.write(final_html)

        print(f"Success! Game compiled to: {out_filepath}")

    except FileNotFoundError:
        print(f"Template file not found at {TEMPLATE_PATH}. Ensure directory structure is correct.")
    except Exception as e:
        print(f"Error during template injection: {e}")

if __name__ == "__main__":
    # create dirs if they don't exist
    os.makedirs(INBOX_DIR, exist_ok=True)
    os.makedirs(HOLODECKS_DIR, exist_ok=True)
    os.makedirs("templates", exist_ok=True)

    # Watch inbox
    watch_inbox()
