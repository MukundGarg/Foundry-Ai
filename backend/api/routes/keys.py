"""
API Key management routes.

Keys are stored in-memory per session token. They are never persisted to disk.
The client sends a session_id header with each request; the server maps that
session_id to a set of provider keys held only in RAM.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from utils.key_store import key_store

router = APIRouter()


class KeysPayload(BaseModel):
    session_id: str
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    google_api_key: Optional[str] = None
    groq_api_key: Optional[str] = None


class KeysResponse(BaseModel):
    session_id: str
    providers_configured: list[str]


@router.post("/set", response_model=KeysResponse)
async def set_keys(payload: KeysPayload):
    """Store API keys for a session."""
    keys: dict[str, str] = {}
    if payload.openai_api_key:
        keys["openai"] = payload.openai_api_key
    if payload.anthropic_api_key:
        keys["anthropic"] = payload.anthropic_api_key
    if payload.google_api_key:
        keys["google"] = payload.google_api_key
    if payload.groq_api_key:
        keys["groq"] = payload.groq_api_key

    if not keys:
        raise HTTPException(status_code=400, detail="At least one API key is required")

    key_store.set(payload.session_id, keys)
    return KeysResponse(
        session_id=payload.session_id,
        providers_configured=list(keys.keys()),
    )


@router.get("/providers/{session_id}", response_model=KeysResponse)
async def get_configured_providers(session_id: str):
    """Return which providers are configured for a session (no key values)."""
    keys = key_store.get(session_id)
    return KeysResponse(
        session_id=session_id,
        providers_configured=list(keys.keys()) if keys else [],
    )


@router.delete("/clear/{session_id}")
async def clear_keys(session_id: str):
    """Remove all keys for a session."""
    key_store.delete(session_id)
    return {"message": "Keys cleared"}
