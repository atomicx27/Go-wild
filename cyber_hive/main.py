import asyncio
import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sse_starlette.sse import EventSourceResponse
from contextlib import asynccontextmanager

from hive_mind import HiveMind

hive_mind = HiveMind()
base_dir = os.path.dirname(__file__)
templates = Jinja2Templates(directory=os.path.join(base_dir, "templates"))


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    task = asyncio.create_task(hive_mind.watch_inbox())
    yield
    # Shutdown
    hive_mind.running = False
    await task

app = FastAPI(title="Cyber Hive", lifespan=lifespan)

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

@app.get("/stream-logs")
async def stream_logs(request: Request):
    async def log_generator():
        while True:
            if await request.is_disconnected():
                break
            try:
                log = await asyncio.wait_for(hive_mind.log_queue.get(), timeout=1.0)
                yield {"data": log}
            except asyncio.TimeoutError:
                continue
    return EventSourceResponse(log_generator())
