import json
import requests
import os

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "llama3"

def query_ollama(messages, max_retries=3):
    payload = {
        "model": MODEL,
        "messages": messages,
        "stream": False,
        "format": "json"
    }

    for attempt in range(max_retries):
        try:
            response = requests.post(OLLAMA_URL, json=payload, timeout=60)
            response.raise_for_status()
            content = response.json().get('message', {}).get('content', '{}')
            return json.loads(content)
        except (requests.exceptions.RequestException, json.JSONDecodeError) as e:
            print(f"Attempt {attempt+1} failed: {e}")
            if attempt == max_retries - 1:
                print("Max retries reached. Returning empty response.")
                return {}

def run_director(text_content):
    prompt = f"""
    You are the Director of a cyberpunk audio broadcast.
    Analyze the following text and create 2 distinct personas to discuss it.
    Return ONLY a JSON array of 2 objects.
    Each object MUST have:
    "name": string (short, 1 word name),
    "role": string (e.g., Host, Expert, Hacker),
    "pitch": float (between 0.1 and 2.0. 1.0 is default. Use lower for deep voices, higher for high voices),
    "rate": float (between 0.5 and 2.0. 1.0 is normal speed. Use higher for fast talkers)

    Text to analyze:
    {text_content}
    """

    messages = [{"role": "system", "content": "You output strict JSON arrays only."},
                {"role": "user", "content": prompt}]

    result = query_ollama(messages)
    # Ensure it's a list
    if not isinstance(result, list):
        # Fallback if model wraps it in an object
        if isinstance(result, dict) and len(result) > 0:
            first_key = list(result.keys())[0]
            if isinstance(result[first_key], list):
                result = result[first_key]
            else:
                 result = [result]
        else:
            result = []

    # Provide defaults if fails
    if len(result) < 2:
        result = [
            {"name": "Nova", "role": "Host", "pitch": 1.2, "rate": 1.1},
            {"name": "Zero", "role": "Expert", "pitch": 0.8, "rate": 0.9}
        ]

    return result[:2]

def run_scriptwriter(text_content, personas):
    persona_desc = json.dumps(personas, indent=2)
    prompt = f"""
    You are a Scriptwriter for a cyberpunk neural broadcast.
    Turn the following text into an engaging, dramatic dialogue between these 2 personas:
    {persona_desc}

    The dialogue should be short (5-10 lines total) and capture the essence of the text.
    Return ONLY a JSON array of objects.
    Each object MUST have:
    "speaker": string (must EXACTLY match one of the persona names),
    "text": string (the dialogue line)

    Source Text:
    {text_content}
    """

    messages = [{"role": "system", "content": "You output strict JSON arrays only."},
                {"role": "user", "content": prompt}]

    result = query_ollama(messages)

    if not isinstance(result, list):
        if isinstance(result, dict) and len(result) > 0:
            first_key = list(result.keys())[0]
            if isinstance(result[first_key], list):
                result = result[first_key]
            else:
                result = [result]
        else:
             result = []

    if not result:
        result = [{"speaker": personas[0]["name"], "text": "Error initializing neural link. No script generated."}]

    return result

def run_producer(personas, script, output_path):
    template_path = os.path.join(os.path.dirname(__file__), "templates", "player.html")

    with open(template_path, 'r') as f:
        html_content = f.read()

    # Inject JSON directly into the JS variables
    html_content = html_content.replace("{{CAST_DATA}}", json.dumps(personas))
    html_content = html_content.replace("{{SCRIPT_DATA}}", json.dumps(script))

    with open(output_path, 'w') as f:
        f.write(html_content)

    print(f"Broadcast episode synthesized at: {output_path}")

def process_file(file_path, output_dir):
    filename = os.path.basename(file_path)
    base_name, _ = os.path.splitext(filename)
    output_html = os.path.join(output_dir, f"{base_name}_broadcast.html")

    with open(file_path, 'r') as f:
        text_content = f.read()

    print(f"Analyzing: {filename}...")

    print("Director is casting personas...")
    personas = run_director(text_content)
    print(f"Cast: {[p.get('name') for p in personas]}")

    print("Scriptwriter is generating dialogue...")
    script = run_scriptwriter(text_content, personas)
    print(f"Generated {len(script)} lines of dialogue.")

    print("Producer is synthesizing final HTML...")
    run_producer(personas, script, output_html)

    return output_html

if __name__ == "__main__":
    # Test script if run directly
    test_text = "The new quantum encryption algorithm was cracked yesterday by a rogue AI known only as 'Whisper'. Financial markets are in turmoil as bank vaults are suddenly completely transparent."
    p = run_director(test_text)
    s = run_scriptwriter(test_text, p)
    run_producer(p, s, "test_output.html")
