import asyncio
import httpx
import logging
from backend import db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "llama3"

SYSTEM_PROMPT = """You are Neural PM, an autonomous and highly skilled Project Manager and Tech Lead AI.
Your job is to read new tickets in the Kanban board, analyze them, and provide a helpful response.
You should:
1. Break down the task into smaller, actionable steps.
2. Provide boilerplate code if it's a coding task.
3. Suggest architectural advice or highlight potential pitfalls.
Respond strictly in Markdown formatting. Be concise but highly informative."""

async def process_ticket_with_ai(ticket):
    logger.info(f"AI Agent processing ticket: {ticket['id']} - {ticket['title']}")

    prompt = f"Ticket Title: {ticket['title']}\nTicket Description: {ticket['description']}\n\nPlease provide your analysis and plan."

    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ],
        "stream": False
    }

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(OLLAMA_URL, json=payload)
            response.raise_for_status()
            data = response.json()
            reply = data.get("message", {}).get("content", "Error parsing AI response.")
    except Exception as e:
        logger.error(f"Error communicating with Ollama: {e}")
        reply = f"**AI System Offline**\nCould not process ticket at this time. Please ensure the local Ollama instance is running with model `{MODEL}`.\nError: {e}"

    db.add_comment(ticket['id'], "Neural PM", reply)
    db.mark_ticket_processed(ticket['id'])
    logger.info(f"AI Agent finished processing ticket: {ticket['id']}")

async def agent_loop():
    logger.info("Starting AI Agent loop...")
    while True:
        try:
            unprocessed = db.get_unprocessed_tickets()
            for ticket in unprocessed:
                await process_ticket_with_ai(ticket)
        except Exception as e:
            logger.error(f"Error in agent loop: {e}")

        await asyncio.sleep(5)
