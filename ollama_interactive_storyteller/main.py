import json
import logging
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import httpx

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

OLLAMA_API_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "qwen2.5:0.5b"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StartRequest(BaseModel):
    genre: str

class ContinueRequest(BaseModel):
    action: str
    context: str

async def generate_response(prompt: str) -> str:
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                OLLAMA_API_URL,
                json={"model": MODEL_NAME, "prompt": prompt, "stream": False},
                timeout=60.0
            )
            response.raise_for_status()
            return response.json()["response"]
        except Exception as e:
            logger.error(f"Error communicating with Ollama: {e}")
            return "Error: Could not connect to the story engine."

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

@app.post("/start")
async def start_story(req: StartRequest):
    prompt = f"""
    You are an interactive storyteller for a {req.genre} adventure.
    Set the scene and provide a brief opening description.
    Then, provide exactly 3 numbered choices for the player to take.
    Format your response EXACTLY like this:

    [Story text here...]

    Choices:
    1. [Choice 1]
    2. [Choice 2]
    3. [Choice 3]
    """
    response_text = await generate_response(prompt)
    return {"text": response_text}

@app.post("/continue")
async def continue_story(req: ContinueRequest):
    prompt = f"""
    You are an interactive storyteller.
    Here is the story so far:
    {req.context}

    The player chose to: {req.action}

    Continue the story based on this action.
    Then, provide exactly 3 numbered choices for the player's next move.
    Format your response EXACTLY like this:

    [New story text here...]

    Choices:
    1. [Choice 1]
    2. [Choice 2]
    3. [Choice 3]
    """
    response_text = await generate_response(prompt)
    return {"text": response_text}
