import json
import logging
import httpx

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "llama3"

SYSTEM_PROMPT = """You are an AI agent that controls a 2D canvas of neural nodes and connections.
You receive the current state of the canvas as JSON, along with a user's prompt.
Your task is to modify the canvas state based on the user's prompt and return the new state as valid JSON.
The JSON should follow this schema:
{
  "nodes": [
    {"id": 1, "label": "Node 1", "color": "#00ff00"}, ...
  ],
  "edges": [
    {"from": 1, "to": 2}, ...
  ]
}
Be creative. Add new nodes, change colors, or connect ideas dynamically. Only return the raw JSON object, no explanation, no markdown blocks.
"""

async def process_canvas_action(current_state: dict, user_prompt: str) -> dict:
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"Current State: {json.dumps(current_state)}\n\nUser Request: {user_prompt}"}
    ]

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                OLLAMA_URL,
                json={"model": MODEL, "messages": messages, "stream": False}
            )
            response.raise_for_status()
            result = response.json()
            content = result["message"]["content"].strip()

            if content.startswith("```json"):
                content = content[7:-3].strip()
            elif content.startswith("```"):
                content = content[3:-3].strip()

            return json.loads(content)
    except Exception as e:
        logger.error(f"Error communicating with Ollama: {e}")
        # Mock fallback for testing or when Ollama is offline
        logger.info("Using mock fallback.")
        new_node_id = len(current_state.get("nodes", [])) + 1
        new_state = current_state.copy()
        new_state.setdefault("nodes", []).append({
            "id": new_node_id,
            "label": f"Fallback: {user_prompt[:10]}...",
            "color": "#ff00ff"
        })
        if new_node_id > 1:
            new_state.setdefault("edges", []).append({
                "from": new_node_id - 1,
                "to": new_node_id
            })
        return new_state
