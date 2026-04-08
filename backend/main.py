from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.resumes import router as resumes_router
from api.user import router as user_router
from api.cover_letter import router as cover_letter_router
from api.application import router as application_router
from api.health import router as health_router
from db.mongodb import close_mongo_connection, connect_to_mongo


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_to_mongo()
    yield
    await close_mongo_connection()


app = FastAPI(
    title="Resume Updater API",
    version="1.0.0",
    lifespan=lifespan,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(health_router)
app.include_router(user_router)
app.include_router(application_router)
app.include_router(resumes_router)
app.include_router(cover_letter_router)


@app.get("/")
async def root():
    return {
        "message": "Resume Updater backend running"
    }
