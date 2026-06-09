from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import os
from agent import process_canvas_action

app = FastAPI(title="Neural Canvas API")

# Absolute path resolution for templates and static files
base_dir = os.path.dirname(os.path.abspath(__file__))
app.mount("/static", StaticFiles(directory=os.path.join(base_dir, "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(base_dir, "templates"))

class ChatRequest(BaseModel):
    prompt: str
    state: dict

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    new_state = await process_canvas_action(request.state, request.prompt)
    return {"status": "success", "state": new_state}
