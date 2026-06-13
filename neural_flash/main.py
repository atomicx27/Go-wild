import os
from fastapi import FastAPI, Depends, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
from datetime import datetime, timedelta

from models import get_db, init_db, Deck, Flashcard

# Initialize database
init_db()

app = FastAPI(title="Neural Flash")

# Setup directories
base_dir = os.path.dirname(__file__)
static_dir = os.path.join(base_dir, "static")
templates_dir = os.path.join(base_dir, "templates")
inbox_dir = os.path.join(base_dir, "inbox")

os.makedirs(static_dir, exist_ok=True)
os.makedirs(templates_dir, exist_ok=True)
os.makedirs(inbox_dir, exist_ok=True)

app.mount("/static", StaticFiles(directory=static_dir), name="static")
templates = Jinja2Templates(directory=templates_dir)

# Pydantic models for responses
class FlashcardResponse(BaseModel):
    id: int
    front: str
    back: str
    box: int

class DeckResponse(BaseModel):
    id: int
    name: str

class AnswerRequest(BaseModel):
    correct: bool

class UploadRequest(BaseModel):
    content: str
    filename: str

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

@app.get("/api/decks", response_model=List[DeckResponse])
def get_decks(db: Session = Depends(get_db)):
    decks = db.query(Deck).all()
    return [{"id": d.id, "name": d.name} for d in decks]

@app.get("/api/decks/{deck_id}/cards", response_model=List[FlashcardResponse])
def get_cards_for_review(deck_id: int, db: Session = Depends(get_db)):
    now = datetime.utcnow()
    # Get cards that are due for review
    cards = db.query(Flashcard).filter(
        Flashcard.deck_id == deck_id,
        Flashcard.next_review <= now
    ).all()

    return [{"id": c.id, "front": c.front, "back": c.back, "box": c.box} for c in cards]

@app.post("/api/cards/{card_id}/answer")
def answer_card(card_id: int, request: AnswerRequest, db: Session = Depends(get_db)):
    card = db.query(Flashcard).filter(Flashcard.id == card_id).first()
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")

    if request.correct:
        # Move up a box (max 5)
        card.box = min(5, card.box + 1)
    else:
        # Reset to box 1
        card.box = 1

    # Calculate next review time based on box
    # Box 1: 1 day, Box 2: 3 days, Box 3: 7 days, Box 4: 14 days, Box 5: 30 days
    delays = {1: 1, 2: 3, 3: 7, 4: 14, 5: 30}
    days = delays.get(card.box, 1)

    card.next_review = datetime.utcnow() + timedelta(days=days)

    db.commit()
    return {"status": "success", "new_box": card.box, "next_review": card.next_review}

@app.post("/api/upload")
def upload_text(request: UploadRequest):
    filepath = os.path.join(inbox_dir, request.filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(request.content)
    return {"status": "success", "message": "File written to inbox"}
