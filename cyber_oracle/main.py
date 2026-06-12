import asyncio
import uuid
import json
import os
from fastapi import FastAPI, BackgroundTasks, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse

from agents.workflow import run_oracle_workflow

app = FastAPI(title="Cyber Oracle API")

# Ensure static directory exists
os.makedirs(os.path.join(os.path.dirname(__file__), "static"), exist_ok=True)
app.mount("/static", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "static")), name="static")

# In-memory job store: mapping job_id to an asyncio.Queue
jobs = {}

class BountyRequest(BaseModel):
    query: str

@app.get("/")
async def root():
    return FileResponse(os.path.join(os.path.dirname(__file__), "static", "index.html"))

@app.post("/api/bounty")
async def create_bounty(request: BountyRequest, background_tasks: BackgroundTasks):
    job_id = str(uuid.uuid4())
    queue = asyncio.Queue()
    jobs[job_id] = queue

    # Start workflow in background
    background_tasks.add_task(execute_job, job_id, request.query)

    return {"job_id": job_id}

async def execute_job(job_id: str, query: str):
    queue = jobs.get(job_id)
    if not queue:
        return

    try:
        await run_oracle_workflow(query, queue)
    except Exception as e:
        await queue.put({"status": "error", "message": f"System Failure: {str(e)}"})

@app.get("/api/stream/{job_id}")
async def stream_status(request: Request, job_id: str):
    queue = jobs.get(job_id)
    if not queue:
        return EventSourceResponse(iter([{"data": json.dumps({"status": "error", "message": "Job not found"})}]), status_code=404)

    async def event_generator():
        while True:
            if await request.is_disconnected():
                break

            try:
                # Wait for next update
                update = await asyncio.wait_for(queue.get(), timeout=1.0)
                yield {"data": json.dumps(update)}

                # Close stream on terminal states
                if update.get("status") in ["complete", "error"]:
                    break
            except asyncio.TimeoutError:
                # Keep-alive
                yield {"data": json.dumps({"status": "ping"})}

        # Cleanup
        if job_id in jobs:
            del jobs[job_id]

    return EventSourceResponse(event_generator())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
