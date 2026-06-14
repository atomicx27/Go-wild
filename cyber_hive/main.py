import os
import asyncio
from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse

from swarm import MissionLog, execute_mission

app = FastAPI(title="Cyber Hive")

templates_dir = os.path.join(os.path.dirname(__file__), 'templates')
templates = Jinja2Templates(directory=templates_dir)

mission_logs = {}

class MissionRequest(BaseModel):
    prompt: str

@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

@app.post("/api/mission")
async def start_mission(request: MissionRequest, background_tasks: BackgroundTasks):
    mission_id = f"mission_{len(mission_logs) + 1}"
    log = MissionLog()
    mission_logs[mission_id] = log

    background_tasks.add_task(execute_mission, request.prompt, log)

    return {"mission_id": mission_id}

@app.get("/api/stream/{mission_id}")
async def stream_mission(mission_id: str, request: Request):
    if mission_id not in mission_logs:
        return {"error": "Mission not found"}

    log = mission_logs[mission_id]

    async def event_generator():
        async for event in log.subscribe():
            if await request.is_disconnected():
                break
            yield event

    return EventSourceResponse(event_generator())
