from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import uvicorn
import re

app = FastAPI()

@app.post("/api/generate")
async def generate(request: Request):
    data = await request.json()
    prompt = data.get("prompt", "")

    print("Mock Ollama received prompt!")

    # Analyze the prompt to see which bug we're fixing
    if "divide(a: int, b: int):" in prompt and "result = a / b" in prompt:
        # Provide a patch for the division by zero bug
        patch = """<<<<<<< SEARCH
    # Intentional bug: Does not handle division by zero
    result = a / b
    return {"result": result}
=======
    # Intentional bug: Does not handle division by zero
    if b == 0:
        return {"error": "Cannot divide by zero"}
    result = a / b
    return {"result": result}
>>>>>>> REPLACE"""
    elif "concat(text: str, times: int):" in prompt and "result = text.append" in prompt:
        patch = """<<<<<<< SEARCH
    # Actually, let's make a real bug: trying to use list method on string
    result = text.append("!")
    return {"result": result}
=======
    # Actually, let's make a real bug: trying to use list method on string
    result = text * times + "!"
    return {"result": result}
>>>>>>> REPLACE"""
    else:
        patch = "I don't know how to fix this."

    return JSONResponse(content={"response": patch})

if __name__ == "__main__":
    print("Starting Mock Ollama Server on port 11434...")
    uvicorn.run(app, host="127.0.0.1", port=11434)
