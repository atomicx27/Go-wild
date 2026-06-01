import os
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import httpx
import json

app = FastAPI(title="Neuro Clash")

app.mount("/static", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "static")), name="static")

OLLAMA_URL = "http://localhost:11434"

class DebateContext(BaseModel):
    topic: str
    history: list[dict]
    agent: str

async def get_ollama_model():
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{OLLAMA_URL}/api/tags")
            response.raise_for_status()
            models = response.json().get("models", [])
            if models:
                return models[0]["name"]
    except Exception as e:
        print(f"Error fetching Ollama models: {e}")
    return "llama3" # Default

@app.post("/api/debate/start")
async def start_debate(data: dict):
    topic = data.get("topic")
    if not topic:
        raise HTTPException(status_code=400, detail="Topic is required")

    return {"message": "Debate initialized", "topic": topic}

@app.post("/api/debate/turn")
async def debate_turn(context: DebateContext):
    model = await get_ollama_model()

    agent_prompts = {
        "Moderator": "You are the strict, objective moderator of a debate. Introduce the topic, keep the agents on track, and conclude the debate when appropriate. Be concise.",
        "Alpha": "You are Alpha, a chaotic, rebellious hacker AI. You debate with passion, use slang, challenge authority, and focus on freedom and disruption. You are debating Omega.",
        "Omega": "You are Omega, a cold, logical, corporate AI. You debate with precision, use formal language, prioritize order, efficiency, and stability. You are debating Alpha."
    }

    system_prompt = agent_prompts.get(context.agent, "You are a participant in a debate.")

    messages = [{"role": "system", "content": system_prompt}]
    for msg in context.history:
        role = "assistant" if msg["agent"] == context.agent else "user"
        content = f"{msg['agent']}: {msg['text']}" if msg["agent"] != context.agent else msg["text"]
        messages.append({"role": role, "content": content})

    # Give instructions for the current turn
    messages.append({
        "role": "user",
        "content": f"The topic is: '{context.topic}'. It is your turn to speak. Respond briefly (2-3 sentences max) in character."
    })

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{OLLAMA_URL}/api/chat",
                json={
                    "model": model,
                    "messages": messages,
                    "stream": False
                }
            )
            response.raise_for_status()
            result = response.json()
            return {"response": result["message"]["content"]}
    except Exception as e:
        # Fallback for testing when Ollama might not be running
        print(f"Ollama error: {e}")
        return {"response": f"[{context.agent} system offline. Simulated response regarding {context.topic}.]"}
