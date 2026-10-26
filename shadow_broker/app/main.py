import asyncio
import threading
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from .database import init_db, get_db, Bounty
from .broker import run_broker_loop
from .merc import run_merc_loop

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB
    init_db()

    # Start background threads for Broker and Mercenary
    broker_thread = threading.Thread(target=run_broker_loop, daemon=True)
    merc_thread = threading.Thread(target=run_merc_loop, daemon=True)

    broker_thread.start()
    merc_thread.start()

    yield

    # Cleanup logic (if any)

app = FastAPI(title="Shadow Broker API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Endpoints
@app.get("/api/bounties")
def get_bounties(db: Session = Depends(get_db)):
    bounties = db.query(Bounty).order_by(Bounty.id.desc()).all()
    return bounties

@app.get("/api/stats")
def get_stats(db: Session = Depends(get_db)):
    total = db.query(Bounty).count()
    completed = db.query(Bounty).filter(Bounty.status == 'COMPLETED').count()
    open_count = db.query(Bounty).filter(Bounty.status == 'OPEN').count()
    return {
        "total_bounties": total,
        "completed_bounties": completed,
        "open_bounties": open_count
    }

# Mount static files at the root
app.mount("/", StaticFiles(directory="/app/shadow_broker/static", html=True), name="static")
