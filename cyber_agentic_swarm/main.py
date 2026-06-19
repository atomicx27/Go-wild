import os
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

app = FastAPI(title="Cyber Agentic Swarm")

templates_dir = os.path.join(os.path.dirname(__file__), "templates")
templates = Jinja2Templates(directory=templates_dir)

class TaskRequest(BaseModel):
    task: str

@app.get("/", response_class=HTMLResponse)
async def get(request: Request):
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

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

from agent import CyberAgent

# A wrapper to allow FastAPI to broadcast to all sockets instead of holding just one
class WebSocketBroadcaster:
    def __init__(self, manager):
        self.manager = manager

    async def send_text(self, text: str):
        await self.manager.broadcast(text)

@app.post("/api/task")
async def execute_task(request: TaskRequest):
    broadcaster = WebSocketBroadcaster(manager)
    agent = CyberAgent(websocket=broadcaster)

    # Run the agent task in the background so we return a response immediately
    asyncio.create_task(agent.run_task(request.task))
    return {"status": "Task accepted. Swarm protocol initiated."}
