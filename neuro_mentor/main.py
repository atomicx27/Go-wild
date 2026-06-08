import asyncio
import json
import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import httpx

from agent import run_agent_loop, DATA_DIR

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Setup directories relative to __file__
BASE_DIR = Path(os.path.dirname(__file__))
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"

OLLAMA_CHAT_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "llama3"

# Start background agent on startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    agent_task = asyncio.create_task(run_agent_loop())
    yield
    agent_task.cancel()
    try:
        await agent_task
    except asyncio.CancelledError:
        pass

app = FastAPI(title="Neuro-Mentor API", lifespan=lifespan)

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

class ChatRequest(BaseModel):
    module_id: str
    message: str
    history: list[dict] = []

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

@app.get("/api/modules")
async def get_modules():
    modules = []
    if DATA_DIR.exists():
        for filepath in DATA_DIR.glob("*.json"):
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    modules.append(data)
            except Exception as e:
                logger.error(f"Error reading module {filepath}: {e}")
    return JSONResponse(content={"modules": modules})

@app.post("/api/chat")
async def chat_with_tutor(request: ChatRequest):
    module_path = DATA_DIR / f"{request.module_id}.json"
    if not module_path.exists():
        raise HTTPException(status_code=404, detail="Module not found")

    try:
        with open(module_path, "r", encoding="utf-8") as f:
            module_data = json.load(f)
    except Exception as e:
        logger.error(f"Error reading module: {e}")
        raise HTTPException(status_code=500, detail="Internal error reading module")

    system_prompt = f"""You are '{module_data.get('persona_name', 'Cyber Tutor')}', an AI tutor with a cyberpunk persona.
You are helping the user learn about the following topic. Stay in character! Keep responses concise and engaging.
Here is the context:
Title: {module_data.get('title')}
Summary: {module_data.get('summary')}
"""

    messages = [{"role": "system", "content": system_prompt}]

    # Append history
    for msg in request.history:
        messages.append({"role": msg.get("role", "user"), "content": msg.get("content", "")})

    messages.append({"role": "user", "content": request.message})

    payload = {
        "model": MODEL_NAME,
        "messages": messages,
        "stream": False
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(OLLAMA_CHAT_URL, json=payload, timeout=60.0)
            response.raise_for_status()
            result = response.json()
            reply = result.get("message", {}).get("content", "Error generating response.")
            return JSONResponse(content={"reply": reply})
    except Exception as e:
        logger.error(f"Ollama chat error: {e}")
        raise HTTPException(status_code=500, detail="Failed to communicate with AI.")
