"""
Foundry AI — Temporal Client
Helper to start workflows from the FastAPI backend.
"""

import json
from temporalio.client import Client
from config import settings
from workflows.mvp_workflow import MVPWorkflow
import structlog

logger = structlog.get_logger()


async def get_temporal_client() -> Client:
    """Get a Temporal client connection."""
    return await Client.connect(
        settings.TEMPORAL_HOST,
        namespace=settings.TEMPORAL_NAMESPACE,
    )


async def start_mvp_workflow(project_id: str, idea: str) -> str:
    """
    Start the MVP generation workflow in Temporal.
    Returns the workflow run ID.
    """
    client = await get_temporal_client()

    handle = await client.start_workflow(
        MVPWorkflow.run,
        args=[project_id, idea],
        id=f"mvp-{project_id}",
        task_queue=settings.TEMPORAL_TASK_QUEUE,
    )

    logger.info(
        "workflow_started",
        project_id=project_id,
        workflow_id=handle.id,
        run_id=handle.result_run_id,
    )

    return handle.result_run_id
