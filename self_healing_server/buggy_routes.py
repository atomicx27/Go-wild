from fastapi import APIRouter

router = APIRouter()

@router.get("/divide")
async def divide(a: int, b: int):
    # Intentional bug: Does not handle division by zero
    result = a / b
    return {"result": result}

@router.get("/concat")
async def concat(text: str, times: int):
    # Intentional bug: Cannot concatenate str and int if user sends wrong type or if python interprets something poorly
    # Or simple typo bug to be fixed
    # Actually, let's make a real bug: trying to use list method on string
    result = text.append("!")
    return {"result": result}

@router.get("/hello")
async def hello():
    return {"message": "Hello, world! Server is alive."}
