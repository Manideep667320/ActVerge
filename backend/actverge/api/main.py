from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from actverge.core.config import settings
from actverge.core.database import init_db
from actverge.api.routes import tasks_router, verdicts_router

logging.basicConfig(level=settings.LOG_LEVEL)
logger = logging.getLogger("actverge")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting ActVerge Application...")
    try:
        await init_db()
        logger.info("Database initialized successfully.")
    except Exception as e:
        logger.warning(f"Could not auto-initialize DB (will retry on migration): {e}")
    yield
    logger.info("Shutting down ActVerge Application...")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    lifespan=lifespan,
    description="ActVerge Agentic AI Outcome-Verification Framework API"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(tasks_router, prefix="/api")
app.include_router(verdicts_router, prefix="/api")

@app.get("/health", tags=["health"])
async def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "llm_selection_status": "PENDING_USER_APPROVAL"
    }
