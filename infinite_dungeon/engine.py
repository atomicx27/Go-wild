import json
import requests

OLLAMA_URL = "http://localhost:11434/api/generate"

class DungeonEngine:
    def __init__(self, model="llama3"):
        self.model = model
        self.state = {
            "health": 100,
            "inventory": ["rusty sword", "health potion"],
            "location": "A dark, damp dungeon cell.",
            "history": []
        }

    def generate_response(self, action):
        prompt = f"""
You are the Game Master of an infinite text adventure.
The player is currently in: {self.state['location']}
Player Health: {self.state['health']}
Player Inventory: {', '.join(self.state['inventory'])}
Recent history: {self.state['history'][-3:] if self.state['history'] else 'None'}

The player performs this action: "{action}"

Respond with a JSON object that describes what happens next. The JSON MUST follow this structure EXACTLY:
{{
    "narrative": "A descriptive, atmospheric paragraph explaining the outcome of the action.",
    "new_location": "A brief description of the new location, or the same location if they didn't move.",
    "health_change": 0, // Integer: negative for damage, positive for healing, 0 for no change
    "item_gained": null, // String of an item name gained, or null
    "item_lost": null // String of an item name lost/used, or null
}}

Do not include any other text, just the JSON.
"""
        try:
            response = requests.post(
                OLLAMA_URL,
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "format": "json",
                    "stream": False,
                },
            )
            response.raise_for_status()
            data = response.json()
            return json.loads(data["response"])
        except Exception as e:
            # Fallback mock for testing or offline mode
            return {
                "narrative": f"The system hiccups and nothing happens. (Error: {e})",
                "new_location": self.state["location"],
                "health_change": 0,
                "item_gained": None,
                "item_lost": None
            }

    def process_action(self, action):
        result = self.generate_response(action)

        # Update state based on AI response
        self.state["history"].append({"action": action, "result": result["narrative"]})
        self.state["location"] = result.get("new_location", self.state["location"])
        self.state["health"] += result.get("health_change", 0)

        if result.get("item_gained"):
            self.state["inventory"].append(result["item_gained"])

        if result.get("item_lost") and result["item_lost"] in self.state["inventory"]:
            self.state["inventory"].remove(result["item_lost"])

        return result
