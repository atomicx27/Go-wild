import os
import json
import asyncio
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

app = FastAPI(title="Cyber Hive")

# Configure Jinja2 templates using absolute path to ensure correct resolution
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Serves the main frontend UI."""
    return templates.TemplateResponse(request=request, name="index.html")


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        # Fire-and-forget approach for broadcasting
        tasks = []
        for connection in self.active_connections:
            tasks.append(connection.send_json(message))
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

manager = ConnectionManager()

# We need to import the agents here avoiding relative import issues if run from cyber_hive directly
import sys
sys.path.append(BASE_DIR)
from agent import QueenAgent, WorkerAgent

async def run_swarm(objective: str):
    """Executes the swarm intelligence workflow."""
    queen = QueenAgent()

    await manager.broadcast({"type": "info", "sender": "SYSTEM", "text": f"Initializing Swarm for objective: '{objective}'"})
    await asyncio.sleep(1) # Simulation delay

    await manager.broadcast({"type": "info", "sender": "QUEEN", "text": "Analyzing objective and breaking down tasks..."})
    tasks = await queen.breakdown_objective(objective)

    await manager.broadcast({"type": "task_list", "sender": "QUEEN", "tasks": tasks})

    for i, task in enumerate(tasks):
        worker = WorkerAgent(f"Drone-{i+1}")
        await manager.broadcast({"type": "info", "sender": f"Drone-{i+1}", "text": f"Received task: {task}"})

        result = await worker.execute_task(task)

        # In a real app we'd save this to the workspace, for now just broadcast it back
        await manager.broadcast({
            "type": "result",
            "sender": f"Drone-{i+1}",
            "task": task,
            "text": f"Completed. Result preview: {result[:100]}..."
        })
        await asyncio.sleep(0.5)

    await manager.broadcast({"type": "success", "sender": "SYSTEM", "text": "Swarm execution complete."})

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            try:
                payload = json.loads(data)
                if payload.get("action") == "dispatch":
                    objective = payload.get("objective")
                    # Fire off the swarm in the background so we don't block the WS
                    asyncio.create_task(run_swarm(objective))
            except json.JSONDecodeError:
                pass
    except WebSocketDisconnect:
        manager.disconnect(websocket)
