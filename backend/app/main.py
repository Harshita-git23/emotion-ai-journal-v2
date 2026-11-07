
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.db.session import Base, engine
from app import models
from app.api.analysis import router as analysis_router
from app.api.auth import router as auth_router
from app.api.experiences import router as experiences_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title=settings.APP_NAME,
    description="A personal emotional history and reflection platform",
    version="1.0.0",
    lifespan=lifespan
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(experiences_router)
app.include_router(analysis_router)


@app.get("/")
def root():
    return {
        "message": "Emotion AI Journal API is running",
        "status": "healthy"
    }


@app.get("/health")
def health():
    return {"status": "ok"}
