from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import threading
import os
import json
import sqlite3

from neon_ledger.database import get_connection, init_db
from neon_ledger.agent import agent_loop

app = FastAPI(title="Neon Ledger")

templates_dir = os.path.join(os.path.dirname(__file__), 'templates')
static_dir = os.path.join(os.path.dirname(__file__), 'static')
templates = Jinja2Templates(directory=templates_dir)

app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.on_event("startup")
def startup_event():
    init_db()
    # Start the agent loop in a background thread
    agent_thread = threading.Thread(target=agent_loop, daemon=True)
    agent_thread.start()

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse(request=request, name='index.html')

@app.get("/api/data")
async def get_data():
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Get latest report
    cursor.execute("SELECT report_text FROM reports ORDER BY created_at DESC LIMIT 1")
    report_row = cursor.fetchone()
    report = report_row['report_text'] if report_row else "<p>Awaiting transaction data in the inbox...</p>"

    # Get transactions
    cursor.execute("SELECT * FROM transactions ORDER BY id DESC")
    transactions = [dict(row) for row in cursor.fetchall()]

    # Get category breakdown
    cursor.execute("SELECT category, SUM(amount) as total FROM transactions GROUP BY category")
    categories = {row['category']: row['total'] for row in cursor.fetchall()}

    conn.close()

    return {
        "report": report,
        "transactions": transactions,
        "categories": categories
    }
