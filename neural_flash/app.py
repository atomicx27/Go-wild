from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import os
import time
from .db import init_db, get_all_cards, get_due_cards, get_card, update_card_review
from .sm2 import calculate_sm2

app = FastAPI()
templates_dir = os.path.join(os.path.dirname(__file__), "templates")
templates = Jinja2Templates(directory=templates_dir)

@app.on_event("startup")
def on_startup():
    init_db()

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    cards = get_all_cards()
    current_time = time.time()
    due_cards = get_due_cards(current_time)

    total_cards = len(cards)
    due_count = len(due_cards)

    return templates.TemplateResponse(request=request, name="index.html", context={
        "total_cards": total_cards,
        "due_count": due_count
    })

@app.get("/review", response_class=HTMLResponse)
async def review_session(request: Request):
    current_time = time.time()
    due_cards = get_due_cards(current_time)

    if not due_cards:
        return RedirectResponse(url="/", status_code=303)

    card = due_cards[0]
    return templates.TemplateResponse(request=request, name="review.html", context={
        "card": card,
        "remaining": len(due_cards)
    })

@app.post("/review/{card_id}")
async def submit_review(card_id: int, quality: int = Form(...)):
    card = get_card(card_id)
    if not card:
        return RedirectResponse(url="/review", status_code=303)

    repetition, interval, ease_factor = calculate_sm2(
        quality,
        card["repetition"],
        card["interval"],
        card["ease_factor"]
    )

    # Next review in seconds (interval is in days)
    next_review = time.time() + (interval * 86400)

    update_card_review(card_id, repetition, interval, ease_factor, next_review)

    return RedirectResponse(url="/review", status_code=303)
