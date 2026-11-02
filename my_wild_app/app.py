import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from duckduckgo_search import DDGS
from langchain_ollama import OllamaLLM
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Initialize Ollama model
llm = OllamaLLM(model="qwen2.5:0.5b")

class ChatRequest(BaseModel):
    message: str

def search_web(query: str, max_results: int = 3) -> str:
    """Searches the web using DuckDuckGo and returns formatted results."""
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))

        if not results:
            return "No web search results found."

        context = "Web Search Results:\n"
        for i, res in enumerate(results):
            context += f"{i+1}. Title: {res.get('title', 'N/A')}\n"
            context += f"   Snippet: {res.get('body', 'N/A')}\n"
            # context += f"   Link: {res.get('href', 'N/A')}\n\n"
        return context
    except Exception as e:
        logger.error(f"Search failed: {e}")
        return "Failed to retrieve web search results."

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

@app.post("/chat")
async def chat_endpoint(req: ChatRequest):
    user_message = req.message
    logger.info(f"Received message: {user_message}")

    # 1. Gather context from web search
    search_context = search_web(user_message)
    logger.info(f"Search context length: {len(search_context)}")

    # 2. Construct prompt for LLM
    prompt = f"""You are Web Weaver, a helpful AI assistant.
Use the following recent web search results to answer the user's question accurately.
If the search results are not relevant, try to answer based on your general knowledge, but mention that.

{search_context}

User Question: {user_message}

Answer clearly and concisely:"""

    # 3. Generate response
    try:
        response = llm.invoke(prompt)
    except Exception as e:
        logger.error(f"LLM generation failed: {e}")
        response = "Sorry, I am having trouble thinking right now. My brain (Ollama) might be offline."

    return {"response": response}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
