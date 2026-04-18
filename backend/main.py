from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from config import settings
from api.routes import workflow, keys, health


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print(f"[Foundry AI] Starting in {settings.app_env} mode")
    yield
    # Shutdown
    print("[Foundry AI] Shutting down")


app = FastAPI(
    title="Foundry AI — Workflow Builder",
    description="AI-powered workflow orchestration platform",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api", tags=["Health"])
app.include_router(keys.router, prefix="/api/keys", tags=["API Keys"])
app.include_router(workflow.router, prefix="/api/workflow", tags=["Workflow"])


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=settings.app_env == "development",
    )
