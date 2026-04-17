"""
Foundry AI — FastAPI Application Entry Point
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import settings
from database import init_db, close_db
import structlog

structlog.configure(
    processors=[
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.dev.ConsoleRenderer(),
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
)

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup and shutdown hooks."""
    logger.info("foundry_ai_starting", env=settings.ENV)
    await init_db()
    logger.info("database_initialized")
    yield
    await close_db()
    logger.info("foundry_ai_shutdown")


app = FastAPI(
    title="Foundry AI",
    description="Meta-AI platform where AI models collaborate to build MVPs",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount routers
from routers.projects import router as projects_router
from routers.websocket import router as ws_router

app.include_router(projects_router)
app.include_router(ws_router)


@app.get("/api/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "foundry-ai",
        "version": "0.1.0",
    }


@app.get("/api/config/models")
async def get_model_config():
    """Return configured AI model information."""
    return {
        "council": {
            "claude": {
                "role": "Architecture & System Design",
                "model": "claude-sonnet-4-20250514",
                "available": bool(settings.ANTHROPIC_API_KEY),
            },
            "gpt": {
                "role": "Product Planning & Task Breakdown",
                "model": "gpt-4o",
                "available": bool(settings.OPENAI_API_KEY),
            },
            "gemini": {
                "role": "Research & Validation",
                "model": "gemini/gemini-2.0-flash",
                "available": bool(settings.GOOGLE_API_KEY),
            },
            "groq": {
                "role": "Fast Evaluation & QA",
                "model": "groq/llama-3.3-70b-versatile",
                "available": bool(settings.GROQ_API_KEY),
            },
        },
        "agents": [
            "DatabaseAgent",
            "BackendAgent",
            "FrontendAgent",
            "DevOpsAgent",
            "IntegrationAgent",
        ],
    }
