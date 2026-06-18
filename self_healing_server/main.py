import traceback
import sys
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.concurrency import run_in_threadpool
import asyncio
import os
import uvicorn
from contextlib import asynccontextmanager

from buggy_routes import router
from healer import heal_code

class SelfHealingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
        except Exception as e:
            tb_str = traceback.format_exc()
            print(f"[!] Unhandled exception caught: {e}")
            print(f"[!] Triggering self-healing agent in background...")

            # Fire and forget the healing process
            asyncio.create_task(heal_code(tb_str))

            return JSONResponse(
                status_code=500,
                content={"error": "Internal Server Error", "message": str(e), "status": "Healing agent deployed. Please try again in a few seconds."}
            )

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Self-Healing Server Starting Up...")
    yield
    print("🛑 Self-Healing Server Shutting Down...")

app = FastAPI(lifespan=lifespan)
app.add_middleware(SelfHealingMiddleware)
app.include_router(router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
