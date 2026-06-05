import httpx
import json

OLLAMA_URL = "http://localhost:11434/api/chat"
DEFAULT_MODEL = "llama3"

async def generate_chat(messages, model=DEFAULT_MODEL):
    """
    Calls the Ollama chat API asynchronously.
    """
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                OLLAMA_URL,
                json={
                    "model": model,
                    "messages": messages,
                    "stream": False
                },
                timeout=60.0
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            return {"error": str(e)}

async def generate_chat_stream(messages, model=DEFAULT_MODEL):
    """
    Calls the Ollama chat API asynchronously and streams the response.
    """
    async with httpx.AsyncClient() as client:
        try:
            async with client.stream(
                "POST",
                OLLAMA_URL,
                json={
                    "model": model,
                    "messages": messages,
                    "stream": True
                },
                timeout=60.0
            ) as response:
                response.raise_for_status()
                async for chunk in response.aiter_text():
                    if chunk:
                        try:
                            # Ollama returns multiple JSON objects per chunk sometimes
                            for line in chunk.strip().split('\n'):
                                if line:
                                    data = json.loads(line)
                                    yield data
                        except json.JSONDecodeError:
                            pass
        except httpx.HTTPError as e:
            yield {"error": str(e)}
