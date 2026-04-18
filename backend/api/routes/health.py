import time
from fastapi import APIRouter
from config import settings

router = APIRouter()

_start_time = time.time()


@router.get("/health")
async def health_check():
    """Liveness probe — returns 200 if the process is alive."""
    return {
        "status": "ok",
        "service": "Foundry AI",
        "env": settings.app_env,
        "uptime_seconds": round(time.time() - _start_time, 1),
    }


@router.get("/ready")
async def readiness_check():
    """Readiness probe — returns 200 when the app is ready to serve traffic."""
    return {"status": "ready"}
