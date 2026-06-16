import httpx
import json
import asyncio
from typing import List, Dict, Any, Optional

OLLAMA_URL = "http://localhost:11434/api/chat"
DEFAULT_MODEL = "llama3"

async def generate_completion(messages: List[Dict[str, str]], model: str = DEFAULT_MODEL) -> str:
    """Helper function to call Ollama chat API."""
    payload = {
        "model": model,
        "messages": messages,
        "stream": False
    }

    async with httpx.AsyncClient(timeout=120.0) as client:
        try:
            response = await client.post(OLLAMA_URL, json=payload)
            response.raise_for_status()
            data = response.json()
            return data.get("message", {}).get("content", "")
        except httpx.HTTPStatusError as e:
            print(f"HTTP error occurred: {e}")
            return ""
        except httpx.RequestError as e:
            print(f"An error occurred while requesting: {e}")
            return ""
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return ""

class QueenAgent:
    """The Queen delegates tasks to Workers based on the objective."""
    def __init__(self):
        self.system_prompt = """You are the Hive Queen. You receive a complex objective and must break it down into a list of specific, actionable sub-tasks for your worker drones.
Output ONLY a valid JSON array of strings, where each string is a distinct task. Do not include any other text or markdown formatting.
Example output:
["Create a robust HTML structure", "Style the page with cyberpunk neon CSS", "Add interactive JS animations"]"""

    async def breakdown_objective(self, objective: str) -> List[str]:
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": f"Objective: {objective}\n\nDeconstruct this into sub-tasks."}
        ]

        response_text = await generate_completion(messages)
        try:
            # Clean up the response in case the LLM wrapped it in markdown code blocks
            clean_text = response_text.replace("```json", "").replace("```", "").strip()
            tasks = json.loads(clean_text)
            if isinstance(tasks, list):
                return tasks
            else:
                return [response_text]
        except json.JSONDecodeError:
            print(f"Failed to parse Queen's output as JSON: {response_text}")
            return [f"Execute task: {objective}"]

class WorkerAgent:
    """A Worker drone that executes a specific task."""
    def __init__(self, role_specialty: str = "general drone"):
        self.specialty = role_specialty
        self.system_prompt = f"""You are a specialized worker drone with expertise in: {self.specialty}.
Your purpose is to complete the given task effectively and provide the result or code snippet.
Be concise but thorough. Focus on the deliverable."""

    async def execute_task(self, task: str) -> str:
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": f"Execute this task: {task}"}
        ]

        result = await generate_completion(messages)
        return result
