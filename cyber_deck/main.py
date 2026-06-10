import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from cyber_deck.agent import CyberDeckAgent

app = FastAPI(title="CyberDeck OS", version="1.0.0")

# Setup paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
WIDGETS_DIR = os.path.join(BASE_DIR, "widgets")

# Mount static files
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Mount templates (using static as templates for simplicity)
templates = Jinja2Templates(directory=STATIC_DIR)

# Initialize Agent
agent = CyberDeckAgent(widgets_dir=WIDGETS_DIR)

class CommandRequest(BaseModel):
    command: str

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

@app.post("/api/execute")
async def execute_command(req: CommandRequest):
    response = await agent.process_command(req.command)
    return {"status": "success", "response": response}

@app.get("/api/widgets")
async def get_widgets():
    return {"status": "success", "widgets": agent.list_widgets()}
