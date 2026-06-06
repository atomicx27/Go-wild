from fastapi import FastAPI, Request, BackgroundTasks, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from contextlib import asynccontextmanager
import json
import httpx

from database import init_db, save_workflow, get_workflows, create_run, get_run_logs, get_workflow
from models import WorkflowRequest, WorkflowResponse, RunResponse
from engine import run_workflow, OLLAMA_API_URL

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(lifespan=lifespan)
import os
templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "templates"))

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

@app.get("/api/workflows")
async def list_workflows():
    return get_workflows()

@app.post("/api/generate_workflow", response_model=WorkflowResponse)
async def generate_workflow(request: WorkflowRequest):
    system_prompt = """You are an AI Architect. The user will give you a goal.
You must output ONLY a raw JSON array of workflow steps to accomplish the goal.
Do not output markdown blocks or any other text.
Each step is an object with:
- id: string
- type: "shell" | "ai" | "write_file"
- content: string (the bash command, prompt, or file content to write. You can use {{prev_output}} to inject previous result)
- target: string (optional, required if type="write_file", the file path)
Example:
[
  {"id": "s1", "type": "shell", "content": "ls -la"},
  {"id": "s2", "type": "ai", "content": "Summarize this: {{prev_output}}"}
]
"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                OLLAMA_API_URL,
                json={
                    "model": "llama3",
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": request.goal}
                    ],
                    "stream": False,
                    "format": "json"
                },
                timeout=120.0
            )
            response.raise_for_status()
            data = response.json()
            raw_content = data["message"]["content"]

            # Basic cleanup in case it added markdown despite instructions
            raw_content = raw_content.strip()
            if raw_content.startswith("```json"):
                raw_content = raw_content[7:]
            if raw_content.endswith("```"):
                raw_content = raw_content[:-3]
            raw_content = raw_content.strip()

            steps = json.loads(raw_content)

            # Save to db
            wf_id = save_workflow(request.goal, steps)

            return WorkflowResponse(id=wf_id, goal=request.goal, steps=steps)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate workflow: {str(e)}")

@app.post("/api/workflows/{workflow_id}/run", response_model=RunResponse)
async def trigger_run(workflow_id: int, background_tasks: BackgroundTasks):
    workflow = get_workflow(workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")

    run_id = create_run(workflow_id)
    background_tasks.add_task(run_workflow, run_id, workflow_id)
    return RunResponse(run_id=run_id, status="running")

@app.get("/api/runs/{run_id}/logs")
async def fetch_logs(run_id: int):
    logs_data = get_run_logs(run_id)
    if logs_data["status"] == "not_found":
        raise HTTPException(status_code=404, detail="Run not found")
    return logs_data
