import os
import json
import httpx
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse

app = FastAPI(title="Cyber Deck OS")

static_dir = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3")

@app.get("/")
async def root():
    return FileResponse(os.path.join(static_dir, "index.html"))

@app.post("/api/chat")
async def chat_endpoint(request: Request):
    data = await request.json()
    messages = data.get("messages", [])

    async def stream_chat():
        async with httpx.AsyncClient() as client:
            try:
                async with client.stream(
                    "POST",
                    f"{OLLAMA_URL}/api/chat",
                    json={"model": OLLAMA_MODEL, "messages": messages, "stream": True},
                    timeout=None
                ) as response:
                    async for line in response.aiter_lines():
                        if line:
                            yield line + "\n"
            except Exception as e:
                yield json.dumps({"error": str(e), "message": {"content": f"Connection error: {e}"}}) + "\n"

    return StreamingResponse(stream_chat(), media_type="application/x-ndjson")

@app.post("/api/forge")
async def forge_endpoint(request: Request):
    data = await request.json()
    prompt = data.get("prompt", "")

    system_prompt = (
        "You are an expert full-stack web developer. "
        "Create a single complete, functional HTML file with embedded CSS and JS inside it based on the user's prompt. "
        "Use modern styling (Tailwind CSS via CDN is fine if you need it, or vanilla CSS). "
        "Make it look cyberpunk or neon if appropriate. "
        "DO NOT use markdown code blocks like ```html in your final output, ONLY return the raw HTML string starting with <!DOCTYPE html> or <html>."
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt}
    ]

    async def stream_forge():
        async with httpx.AsyncClient() as client:
            try:
                async with client.stream(
                    "POST",
                    f"{OLLAMA_URL}/api/chat",
                    json={"model": OLLAMA_MODEL, "messages": messages, "stream": True},
                    timeout=None
                ) as response:
                    async for line in response.aiter_lines():
                        if line:
                            yield line + "\n"
            except Exception as e:
                yield json.dumps({"error": str(e), "message": {"content": f"Connection error: {e}"}}) + "\n"

    return StreamingResponse(stream_forge(), media_type="application/x-ndjson")
