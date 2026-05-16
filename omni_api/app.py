from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import traceback
from endpoints import router
import omni_healer

app = FastAPI(title="Omni API", description="A self-writing API.")

app.include_router(router)

@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request: Request, exc: StarletteHTTPException):
    if exc.status_code == 404:
        method = request.method
        path = request.url.path

        background_tasks = BackgroundTasks()
        background_tasks.add_task(omni_healer.generate_endpoint, method, path)

        print(f"[App] 404 hit for {method} {path}. Queuing background generation task.")

        return JSONResponse(
            status_code=202,
            content={"message": f"Endpoint {method} {path} not found. Omni Healer is generating it now. Please try again in a few seconds."},
            background=background_tasks
        )
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

@app.exception_handler(404)
async def custom_404_handler(request: Request, exc: Exception):
    method = request.method
    path = request.url.path

    # Run the generator in the background
    background_tasks = BackgroundTasks()
    background_tasks.add_task(omni_healer.generate_endpoint, method, path)

    # Debugging output to verify background task is requested
    print(f"[App] 404 hit for {method} {path}. Queuing background generation task.")

    return JSONResponse(
        status_code=202,
        content={"message": f"Endpoint {method} {path} not found. Omni Healer is generating it now. Please try again in a few seconds."},
        background=background_tasks
    )

@app.exception_handler(Exception)
async def custom_500_handler(request: Request, exc: Exception):
    # Capture the full traceback
    tb = traceback.format_exc()

    # Run the healer in the background
    background_tasks = BackgroundTasks()
    background_tasks.add_task(omni_healer.heal_runtime_error, tb)

    print(f"[App] 500 hit. Queuing background repair task.")

    return JSONResponse(
        status_code=500,
        content={
            "message": "Internal Server Error. Omni Healer has been dispatched to fix the bug. Please try again in a few seconds.",
            "error": str(exc)
        },
        background=background_tasks
    )
