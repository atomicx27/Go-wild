from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional
import uuid
import os
import asyncio
from contextlib import asynccontextmanager

from backend import db
from backend import agent

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Setup DB
    db.init_db()

    # Start AI Agent
    task = asyncio.create_task(agent.agent_loop())

    yield

    # Teardown
    task.cancel()

app = FastAPI(lifespan=lifespan)

class TicketCreate(BaseModel):
    title: str
    description: str
    status: str = "TODO"

class TicketStatusUpdate(BaseModel):
    status: str

class CommentCreate(BaseModel):
    author: str
    content: str

@app.get("/api/tickets")
def get_tickets():
    return db.get_tickets()

@app.post("/api/tickets")
def create_ticket(ticket: TicketCreate):
    ticket_id = str(uuid.uuid4())
    db.add_ticket(ticket_id, ticket.title, ticket.description, ticket.status)
    return {"id": ticket_id, "message": "Ticket created"}

@app.put("/api/tickets/{ticket_id}/status")
def update_ticket_status(ticket_id: str, update: TicketStatusUpdate):
    ticket = db.get_ticket(ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    db.update_ticket_status(ticket_id, update.status)
    return {"message": "Status updated"}

@app.get("/api/tickets/{ticket_id}/comments")
def get_comments(ticket_id: str):
    ticket = db.get_ticket(ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return db.get_comments(ticket_id)

@app.post("/api/tickets/{ticket_id}/comments")
def add_comment(ticket_id: str, comment: CommentCreate):
    ticket = db.get_ticket(ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    db.add_comment(ticket_id, comment.author, comment.content)
    return {"message": "Comment added"}

# Mount frontend
frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
if os.path.exists(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")
