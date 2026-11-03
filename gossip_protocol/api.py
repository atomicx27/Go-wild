from fastapi import FastAPI, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from db import get_db, Agent, Memory, Conversation

app = FastAPI(title="Gossip Protocol API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/agents")
def read_agents(db: Session = Depends(get_db)):
    agents = db.query(Agent).all()
    return [{"id": a.id, "name": a.name, "persona": a.persona} for a in agents]

@app.get("/api/agents/{agent_id}/memories")
def read_memories(agent_id: int, db: Session = Depends(get_db)):
    memories = db.query(Memory).filter(Memory.agent_id == agent_id).order_by(Memory.timestamp.desc()).all()
    return [{"id": m.id, "content": m.content, "timestamp": m.timestamp} for m in memories]

@app.get("/api/conversations")
def read_conversations(limit: int = 10, db: Session = Depends(get_db)):
    conversations = db.query(Conversation).order_by(Conversation.timestamp.desc()).limit(limit).all()
    return [{
        "id": c.id,
        "transcript": c.transcript,
        "timestamp": c.timestamp,
        "agent1_id": c.agent1_id,
        "agent2_id": c.agent2_id
    } for c in conversations]

app.mount("/", StaticFiles(directory="static", html=True), name="static")
