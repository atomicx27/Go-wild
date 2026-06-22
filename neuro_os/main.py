from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from contextlib import asynccontextmanager
import asyncio
import os
from pydantic import BaseModel
from agent import KernelAgent

agent = KernelAgent()

@asynccontextmanager
async def lifespan(app: FastAPI):
    await agent.start()
    yield
    await agent.stop()

app = FastAPI(lifespan=lifespan)

static_dir = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/")
async def root():
    return FileResponse(os.path.join(static_dir, "index.html"))

@app.get("/api/fs/desktop")
async def list_desktop():
    try:
        files = os.listdir(agent.desktop_dir)
        return {"files": files}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.get("/api/fs/read/{filename}")
async def read_file(filename: str):
    filepath = agent.desktop_dir / filename
    if not filepath.exists():
        return JSONResponse(status_code=404, content={"error": "File not found"})
    try:
        with open(filepath, "r") as f:
            content = f.read()
        return {"content": content}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

class ChatRequest(BaseModel):
    message: str

@app.post("/api/chat")
async def chat(request: ChatRequest):
    response = await agent.handle_chat(request.message)
    return {"response": response}

@app.websocket("/ws/thoughts")
async def websocket_thoughts(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            thought = await agent.thoughts_queue.get()
            await websocket.send_text(thought)
    except WebSocketDisconnect:
        pass
    except Exception as e:
        print(f"WebSocket error: {e}")
