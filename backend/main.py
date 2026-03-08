from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from core.config import settings
from db.mongodb import connect_to_mongo, close_mongo_connection
from api import health, resumes, user, application

@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_to_mongo()
    yield
    await close_mongo_connection()


app = FastAPI(
    title="Resume Updater API",
    description="Backend API for Resume Updater application",
    version="1.0.0",
    lifespan=lifespan
)

# main.py (add after `app = FastAPI()`)

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger("uvicorn.error")

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # Try to read request body safely
    try:
        body = await request.json()
    except Exception:
        # If body is not JSON or already read, attempt to get raw bytes
        try:
            body = (await request.body()).decode("utf-8", errors="replace")
        except Exception:
            body = "<could not parse body>"
    # Log details to console with full context
    logger.error("RequestValidationError: %s %s\nRequest body: %s\nErrors: %s",
                 request.method, request.url.path, body, exc.errors())
    # Return the default JSON response so client still sees the 422
    return JSONResponse(status_code=422, content={"detail": exc.errors()})

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(resumes.router)
app.include_router(user.router)
app.include_router(application.router)


@app.get("/")
async def root():
    return {
        "message": "Welcome to Resume Updater API",
        "docs": "/docs",
        "health": "/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
