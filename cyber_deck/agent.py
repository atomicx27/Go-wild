import json
import os
import httpx

OLLAMA_URL = "http://localhost:11434/api/chat"

class CyberDeckAgent:
    def __init__(self, widgets_dir: str):
        self.widgets_dir = widgets_dir
        if not os.path.exists(self.widgets_dir):
            os.makedirs(self.widgets_dir, exist_ok=True)

        self.system_prompt = """You are the core intelligence of 'CyberDeck OS', a neon cyberpunk-themed desktop environment.
Your goal is to process user commands and translate them into actionable responses or widgets.
You can create HTML/JS/CSS widgets that will be rendered on the desktop.
If the user asks for a tool (like a calculator, weather app, notes, or mini-game), output valid JSON that describes the widget.

Response format MUST be valid JSON:
{
  "type": "widget_creation",
  "name": "widget_name",
  "html": "<div class='p-4 text-neon-green'>...</div>",
  "message": "I have created the widget for you."
}

If no widget is needed, just respond with:
{
  "type": "chat",
  "message": "Your response here."
}
"""

    async def process_command(self, command: str) -> dict:
        payload = {
            "model": "llama3",
            "messages": [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": command}
            ],
            "stream": False,
            "format": "json"
        }
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(OLLAMA_URL, json=payload, timeout=30.0)
                response.raise_for_status()
                data = response.json()
                content = data["message"]["content"]

                try:
                    parsed = json.loads(content)

                    if parsed.get("type") == "widget_creation":
                        self._save_widget(parsed)

                    return parsed
                except json.JSONDecodeError:
                    return {"type": "error", "message": "Failed to parse Ollama response as JSON.", "raw": content}

        except Exception as e:
            return {"type": "error", "message": f"Ollama connection error: {str(e)}"}

    def _save_widget(self, widget_data: dict):
        name = widget_data.get("name", "unknown_widget").replace(" ", "_").lower()
        html = widget_data.get("html", "<div>Error generating widget HTML</div>")

        filepath = os.path.join(self.widgets_dir, f"{name}.html")
        with open(filepath, "w") as f:
            f.write(html)

    def list_widgets(self):
        widgets = []
        if os.path.exists(self.widgets_dir):
            for file in os.listdir(self.widgets_dir):
                if file.endswith(".html"):
                    with open(os.path.join(self.widgets_dir, file), "r") as f:
                        widgets.append({
                            "name": file.replace(".html", ""),
                            "html": f.read()
                        })
        return widgets
