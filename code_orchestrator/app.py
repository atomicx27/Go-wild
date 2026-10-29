from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import requests
import json
import uvicorn
import os

app = FastAPI()

# Make templates dir
os.makedirs("templates", exist_ok=True)
os.makedirs("static", exist_ok=True)

# Templates setup
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

OLLAMA_URL = "http://localhost:11434/api/generate"

def ask_ollama(prompt, model="qwen2.5:0.5b", system="You are an intelligent code orchestrator assistant."):
    payload = {
        "model": model,
        "prompt": prompt,
        "system": system,
        "stream": False
    }

    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=60)
        response.raise_for_status()
        return response.json().get("response", "")
    except Exception as e:
        return f"Error communicating with Ollama: {str(e)}"

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/chat")
async def chat(prompt: str = Form(...)):
    # 1. First, let the agent think about the problem
    thinking_prompt = f"Given this user request: '{prompt}', explain your step-by-step plan to resolve it. Be concise."
    plan = ask_ollama(thinking_prompt)

    # 2. Then, let the agent execute the solution
    execution_prompt = f"The user request is: '{prompt}'. The plan is: '{plan}'. Now, provide the final implementation or answer. Only output code or the direct answer."
    result = ask_ollama(execution_prompt)

    return JSONResponse({
        "plan": plan,
        "result": result
    })

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
