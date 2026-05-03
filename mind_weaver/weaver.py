import json
import urllib.request
import urllib.error

class OllamaClient:
    def __init__(self, host="http://localhost:11434", model="llama3"):
        self.host = host
        self.model = model
        self.api_url = f"{self.host}/api/generate"

    def generate(self, prompt, system="", format=""):
        data = {
            "model": self.model,
            "prompt": prompt,
            "system": system,
            "stream": False
        }
        if format:
            data["format"] = format

        req = urllib.request.Request(
            self.api_url,
            data=json.dumps(data).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )

        try:
            with urllib.request.urlopen(req) as response:
                result = json.loads(response.read().decode("utf-8"))
                return result.get("response", "")
        except urllib.error.URLError as e:
            print(f"[OllamaClient] Error connecting to Ollama: {e}")
            return self._mock_response(prompt, format)

    def _mock_response(self, prompt, format):
        """Fallback response if Ollama is unreachable."""
        print("[OllamaClient] Returning mock response due to connection failure.")
        if format == "json":
            # Very basic mock logic that tries to fit the categorization
            if "def " in prompt or "import " in prompt:
                return json.dumps({
                    "category": "code",
                    "title": "Mock Code Snippet",
                    "summary": "This looks like code.",
                    "action_items": []
                })
            elif "todo" in prompt.lower() or "task" in prompt.lower():
                return json.dumps({
                    "category": "journal",
                    "title": "Mock Journal Entry",
                    "summary": "A mock journal entry with tasks.",
                    "action_items": ["Mock Task 1"]
                })
            elif "Related Links" in prompt:
                return json.dumps({"links": ["Mock Relation"]})
            else:
                return json.dumps({
                    "category": "concept",
                    "title": "Mock Concept",
                    "summary": "A generic mock concept.",
                    "action_items": []
                })
        return "This is a mock response from Mind Weaver fallback."

import os
import shutil

INBOX_DIR = "mind_weaver/inbox"
VAULT_DIR = "mind_weaver/vault"

def analyze_content(client, content):
    system_prompt = """
    You are a Second Brain organizer. Analyze the following raw text and extract:
    1. 'category': Must be exactly one of 'code', 'journal', or 'concept'.
    2. 'title': A short, descriptive title.
    3. 'summary': A 1-2 sentence summary.
    4. 'action_items': A list of any tasks, todos, or action items found. Empty list if none.

    Respond STRICTLY in JSON format matching this schema. Do not include markdown formatting like ```json in the output.
    """

    response = client.generate(
        prompt=content,
        system=system_prompt,
        format="json"
    )

    try:
        return json.loads(response)
    except json.JSONDecodeError:
        print("[Weaver] Failed to decode JSON from Ollama. Using fallback.")
        return client._mock_response(content, "json")


def process_inbox():
    client = OllamaClient()
    if not os.path.exists(INBOX_DIR):
        print(f"[Weaver] Inbox directory {INBOX_DIR} not found.")
        return

    for filename in os.listdir(INBOX_DIR):
        filepath = os.path.join(INBOX_DIR, filename)
        if not os.path.isfile(filepath):
            continue

        print(f"[Weaver] Processing {filename}...")
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        analysis = analyze_content(client, content)
        if isinstance(analysis, str):
            try:
               analysis = json.loads(analysis)
            except:
               print(f"[Weaver] Failed to process {filename} fallback logic.")
               continue

        print(f"[Weaver] Analyzed {filename}: {analysis.get('title')}")

        category = analysis.get("category", "concept")
        if category not in ["code", "journal", "concept"]:
            category = "concept"

        title = analysis.get("title", "Untitled").replace("/", "-").replace(" ", "_")
        summary = analysis.get("summary", "")
        action_items = analysis.get("action_items", [])

        # Format as Markdown
        md_content = f"# {analysis.get('title', 'Untitled')}\n\n"
        md_content += f"**Category:** {category}\n\n"
        md_content += f"**Summary:** {summary}\n\n"
        md_content += "---\n\n"

        if category == "code":
             md_content += "```\n" + content + "\n```\n"
        else:
             md_content += content + "\n\n"

        if action_items:
             md_content += "---\n\n### Action Items\n"
             for item in action_items:
                 md_content += f"- [ ] {item}\n"

        # Route file
        dest_dir = os.path.join(VAULT_DIR, category)
        if category == "concept":
             dest_dir = os.path.join(VAULT_DIR, "concepts")

        dest_filename = f"{title}.md"
        dest_path = os.path.join(dest_dir, dest_filename)

        with open(dest_path, "w", encoding="utf-8") as f:
             f.write(md_content)

        # Append to KANBAN
        if action_items:
            kanban_path = os.path.join(VAULT_DIR, "KANBAN.md")
            with open(kanban_path, "a", encoding="utf-8") as f:
                f.write(f"\n### Source: [[{title}]]\n")
                for item in action_items:
                    f.write(f"- [ ] {item}\n")

        if category == "concept":
             update_index(title, summary)
             cross_reference_concept(client, dest_path, title, summary)

        # Remove original file
        os.remove(filepath)
        print(f"[Weaver] Moved to {dest_path} and updated KANBAN if needed.")

def update_index(concept_title, summary):
    index_path = os.path.join(VAULT_DIR, "INDEX.md")

    # Read existing index to avoid duplicates (basic check)
    if os.path.exists(index_path):
        with open(index_path, "r", encoding="utf-8") as f:
            content = f.read()
            if f"[[{concept_title}]]" in content:
                return

    with open(index_path, "a", encoding="utf-8") as f:
        if os.path.getsize(index_path) == 0:
            f.write("# Vault Index\n\n")
        f.write(f"- [[{concept_title}]]: {summary}\n")
    print(f"[Weaver] Updated INDEX.md with {concept_title}")


def cross_reference_concept(client, concept_file_path, concept_title, summary):
    index_path = os.path.join(VAULT_DIR, "INDEX.md")
    if not os.path.exists(index_path):
        return

    with open(index_path, "r", encoding="utf-8") as f:
        index_content = f.read()

    system_prompt = """
    You are a knowledge manager. You are given a new concept and an INDEX of existing concepts.
    Your task is to find existing concepts in the INDEX that are semantically related to the new concept.

    Respond STRICTLY in JSON format with a single key 'links' containing a list of exactly matched titles of related concepts from the INDEX.
    Do not include the new concept itself. Empty list if none match.
    Do not include markdown formatting like ```json in the output.
    """

    prompt = f"New Concept: {concept_title}\nSummary: {summary}\n\nINDEX:\n{index_content}"

    response = client.generate(prompt=prompt, system=system_prompt, format="json")
    try:
        data = json.loads(response)
        links = data.get("links", [])
    except json.JSONDecodeError:
         print(f"[Weaver] Failed to decode JSON for auto-linking {concept_title}. Using fallback.")
         fallback = client._mock_response(prompt, "json")
         try:
             data = json.loads(fallback)
             links = data.get("links", [])
         except:
             links = []

    if links:
        print(f"[Weaver] Auto-linking {concept_title} to {links}")
        # Append links to the new file
        with open(concept_file_path, "a", encoding="utf-8") as f:
            f.write("\n---\n**Related Links:**\n")
            for link in links:
                if link != concept_title:
                   f.write(f"- [[{link}]]\n")

        # Append reciprocal link to the related files
        for link in links:
            if link == concept_title:
                 continue
            linked_file = os.path.join(VAULT_DIR, "concepts", f"{link}.md")
            if os.path.exists(linked_file):
                with open(linked_file, "a", encoding="utf-8") as f:
                    f.write(f"\n- [[{concept_title}]] (Auto-linked reciprocal)\n")

if __name__ == "__main__":
    print("[Weaver] Starting Mind Weaver processing...")
    process_inbox()
    print("[Weaver] Finished processing.")
