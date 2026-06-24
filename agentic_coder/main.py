import os
import asyncio
from fastapi import FastAPI, WebSocket, Request, BackgroundTasks
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn

from agent import run_agent, WORKSPACE_DIR

app = FastAPI()

app.mount("/static", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "static")), name="static")

class PromptRequest(BaseModel):
    prompt: str

# Store connected websockets to broadcast updates
active_connections = []

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)
    try:
        while True:
            await websocket.receive_text()
    except Exception:
        active_connections.remove(websocket)

async def broadcast_message(message: str):
    for connection in active_connections:
        try:
            await connection.send_text(message)
        except Exception:
            pass

@app.get("/", response_class=HTMLResponse)
async def get_index():
    with open(os.path.join(os.path.dirname(__file__), "static", "index.html"), "r") as f:
        return f.read()

@app.post("/run")
async def run_prompt(req: PromptRequest, background_tasks: BackgroundTasks):
    async def task():
        try:
            await run_agent(req.prompt, callback=broadcast_message)
        except Exception as e:
            await broadcast_message(f"Error: {str(e)}")

    background_tasks.add_task(task)
    return {"status": "started"}

@app.get("/workspace_files")
async def get_workspace_files():
    files_data = {}
    if os.path.exists(WORKSPACE_DIR):
        for filename in os.listdir(WORKSPACE_DIR):
            filepath = os.path.join(WORKSPACE_DIR, filename)
            if os.path.isfile(filepath):
                with open(filepath, "r") as f:
                    files_data[filename] = f.read()
    return JSONResponse(content=files_data)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
