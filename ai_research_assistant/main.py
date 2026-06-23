import asyncio
import json
import os
import requests
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import AsyncGenerator

app = FastAPI(title="Autonomous AI Research Assistant")

# Use absolute path for templates to avoid CWD issues
base_dir = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(base_dir, "templates"))

OLLAMA_API_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "qwen2.5:0.5b"

class ResearchRequest(BaseModel):
    topic: str

def query_ollama(prompt: str) -> str:
    """Synchronous call to local Ollama API."""
    try:
        payload = {
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False
        }
        response = requests.post(OLLAMA_API_URL, json=payload, timeout=60)
        response.raise_for_status()
        return response.json().get("response", "").strip()
    except Exception as e:
        return f"Error querying Ollama: {str(e)}"

def search_wikipedia(query: str) -> str:
    """Fetch summary from Wikipedia."""
    try:
        search_url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={requests.utils.quote(query)}&utf8=&format=json"
        search_res = requests.get(search_url, timeout=10).json()
        search_results = search_res.get("query", {}).get("search", [])

        if not search_results:
            return "No Wikipedia results found."

        title = search_results[0]["title"]
        page_url = f"https://en.wikipedia.org/w/api.php?action=query&prop=extracts&exintro&explaintext&titles={requests.utils.quote(title)}&format=json"
        page_res = requests.get(page_url, timeout=10).json()
        pages = page_res.get("query", {}).get("pages", {})

        for page_id in pages:
            extract = pages[page_id].get("extract", "")
            if extract:
                return f"Wikipedia Summary for {title}: {extract}"
        return "Failed to extract Wikipedia summary."
    except Exception as e:
        return f"Error fetching Wikipedia data: {str(e)}"

async def research_agent_orchestrator(topic: str) -> AsyncGenerator[str, None]:
    """Agent orchestrator that yields progress steps as SSE."""
    def create_sse_event(action: str, data: str) -> str:
        # We encode data to JSON to ensure it handles newlines correctly in SSE format
        payload = json.dumps({"action": action, "data": data})
        return f"data: {payload}\n\n"

    yield create_sse_event("status", f"Starting research on topic: {topic}")
    await asyncio.sleep(1)

    import re

    # Step 1: Brainstorming
    yield create_sse_event("status", "Brainstorming search queries...")
    brainstorm_prompt = f"I need to research the topic '{topic}'. Provide 3 specific search queries to find factual information on this. Output ONLY a comma-separated list of queries."
    queries_text = query_ollama(brainstorm_prompt)

    # More robust parsing to handle smaller models that might output numbered lists instead of comma separated
    if ',' in queries_text and '\n' not in queries_text:
         queries = [q.strip() for q in queries_text.split(",") if q.strip()][:3]
    else:
         lines = [line.strip() for line in queries_text.split('\n') if line.strip()]
         queries = []
         for line in lines:
             clean_line = re.sub(r'^\d+\.\s*', '', line).strip()
             clean_line = clean_line.strip('"').strip("'").strip('*')
             if clean_line:
                 queries.append(clean_line)
         queries = queries[:3]

    if not queries:
        queries = [topic]

    yield create_sse_event("log", f"Generated queries: {queries}")
    await asyncio.sleep(1)

    # Step 2: Information Gathering
    yield create_sse_event("status", "Gathering information from Wikipedia...")
    gathered_data = []
    for q in queries:
        yield create_sse_event("log", f"Searching for: {q}")
        wiki_text = search_wikipedia(q)
        gathered_data.append(f"Source ({q}): {wiki_text[:500]}...") # Keep it somewhat brief
        yield create_sse_event("log", f"Found data for '{q}': {wiki_text[:100]}...")
        await asyncio.sleep(0.5)

    # Step 3: Synthesis
    yield create_sse_event("status", "Synthesizing research report...")
    combined_context = "\n".join(gathered_data)
    report_prompt = f"You are an expert AI researcher. Based on the following information, write a concise, well-structured markdown report about '{topic}'. Use headings and bullet points.\n\nInformation:\n{combined_context}\n\nMarkdown Report:"

    # We will simulate a streaming response from Ollama for the final report to make it look cool,
    # but for simplicity in this orchestrator, we fetch it all at once and yield it.
    # To truly stream the ollama response over SSE, we would use stream=True in requests.
    try:
        payload = {
            "model": MODEL_NAME,
            "prompt": report_prompt,
            "stream": True
        }
        with requests.post(OLLAMA_API_URL, json=payload, stream=True, timeout=120) as r:
            r.raise_for_status()
            yield create_sse_event("report_start", "Starting report generation...")
            for line in r.iter_lines():
                if line:
                    decoded_line = line.decode('utf-8')
                    try:
                        chunk_data = json.loads(decoded_line)
                        chunk_text = chunk_data.get("response", "")
                        if chunk_text:
                            yield create_sse_event("report_chunk", chunk_text)
                    except json.JSONDecodeError:
                        pass
    except Exception as e:
         yield create_sse_event("error", f"Error generating report: {str(e)}")

    yield create_sse_event("status", "Research complete!")
    yield create_sse_event("done", "")


@app.get("/", response_class=HTMLResponse)
async def get_index(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

@app.get("/api/research")
async def perform_research(topic: str):
    return StreamingResponse(
        research_agent_orchestrator(topic),
        media_type="text/event-stream"
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
