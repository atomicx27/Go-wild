import asyncio
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MissionLog:
    def __init__(self):
        self.queue = asyncio.Queue()

    async def log(self, event_type: str, message: str, data: dict = None):
        event = {
            "type": event_type,
            "message": message,
            "data": data or {}
        }
        await self.queue.put(event)

    async def subscribe(self):
        while True:
            event = await self.queue.get()
            yield f"data: {json.dumps(event)}\n\n"

import httpx

OLLAMA_API = "http://localhost:11434/api/chat"

async def queen_agent(prompt: str, mission_log: MissionLog):
    await mission_log.log("queen_start", f"Queen analyzing prompt: {prompt}")
    try:
        async with httpx.AsyncClient() as client:
            system_prompt = (
                "You are the Queen of an AI Swarm. Your task is to break down the user's prompt "
                "into exactly 3 distinct, actionable subtasks. Respond ONLY with a valid JSON array of strings, "
                "with no additional text or markdown formatting. Example: [\"Task 1\", \"Task 2\", \"Task 3\"]"
            )
            response = await client.post(
                OLLAMA_API,
                json={
                    "model": "llama3",
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    "stream": False
                },
                timeout=30.0
            )
            response.raise_for_status()
            data = response.json()
            content = data["message"]["content"].strip()

            # Simple cleanup in case ollama returns markdown
            if content.startswith("```json"):
                content = content[7:]
            if content.endswith("```"):
                content = content[:-3]

            subtasks = json.loads(content.strip())

            if not isinstance(subtasks, list):
                raise ValueError("Response is not a JSON list")

            await mission_log.log("queen_complete", "Queen generated subtasks", {"subtasks": subtasks})
            return subtasks

    except Exception as e:
        logger.error(f"Queen Agent error: {e}")
        await mission_log.log("queen_error", f"Queen Agent encountered an error: {e}")
        return [f"Fallback task 1 for {prompt}", f"Fallback task 2 for {prompt}"]

async def drone_agent(drone_id: int, task: str, mission_log: MissionLog):
    await mission_log.log("drone_start", f"Drone {drone_id} started task: {task}", {"drone_id": drone_id, "task": task})
    try:
        async with httpx.AsyncClient() as client:
            system_prompt = (
                f"You are Drone {drone_id} of an AI Swarm. Your task is to execute the following subtask. "
                "Provide a brief, single-paragraph summary of your execution."
            )
            response = await client.post(
                OLLAMA_API,
                json={
                    "model": "llama3",
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": task}
                    ],
                    "stream": False
                },
                timeout=45.0
            )
            response.raise_for_status()
            data = response.json()
            result = data["message"]["content"].strip()

            await mission_log.log("drone_complete", f"Drone {drone_id} completed task", {"drone_id": drone_id, "task": task, "result": result})
            return result
    except Exception as e:
        logger.error(f"Drone {drone_id} error: {e}")
        await mission_log.log("drone_error", f"Drone {drone_id} encountered an error: {e}", {"drone_id": drone_id})
        return f"Drone {drone_id} executed fallback for task."


async def execute_mission(prompt: str, mission_log: MissionLog):
    await mission_log.log("mission_start", "Mission started", {"prompt": prompt})

    subtasks = await queen_agent(prompt, mission_log)

    tasks = []
    for i, subtask in enumerate(subtasks):
        tasks.append(drone_agent(i + 1, subtask, mission_log))

    results = await asyncio.gather(*tasks)

    await mission_log.log("mission_complete", "Mission complete", {"results": results})
