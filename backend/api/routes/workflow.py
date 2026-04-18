"""
Workflow routes — the main entry point for the AI Workflow Builder.
"""

import traceback
from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel
from typing import Optional

from workflows.engine import WorkflowEngine
from utils.key_store import key_store
from utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()


class WorkflowRequest(BaseModel):
    idea: str
    session_id: str
    preferred_provider: Optional[str] = None  # openai | anthropic | google | groq


class WorkflowStatusRequest(BaseModel):
    workflow_id: str
    session_id: str


@router.post("/run")
async def run_workflow(request: WorkflowRequest):
    """
    Main endpoint: takes a user idea, plans tasks, assigns agents,
    executes the workflow, and returns the aggregated result.
    """
    keys = key_store.get(request.session_id)
    if not keys:
        raise HTTPException(
            status_code=401,
            detail="No API keys found for this session. Please configure keys first.",
        )

    engine = WorkflowEngine(api_keys=keys)
    try:
        result = await engine.run(
            idea=request.idea,
            preferred_provider=request.preferred_provider,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Workflow execution failed:\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Workflow execution failed: {str(e)}")


@router.post("/plan")
async def plan_only(request: WorkflowRequest):
    """
    Returns the workflow plan (tasks + agent assignments) without executing.
    Useful for previewing the workflow graph before running.
    """
    keys = key_store.get(request.session_id)
    if not keys:
        raise HTTPException(
            status_code=401,
            detail="No API keys found for this session.",
        )

    engine = WorkflowEngine(api_keys=keys)
    try:
        plan = await engine.plan(
            idea=request.idea,
            preferred_provider=request.preferred_provider,
        )
        return plan
    except Exception as e:
        logger.error(f"Planning failed:\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Planning failed: {str(e)}")
