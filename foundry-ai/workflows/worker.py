"""
Foundry AI — Temporal Worker
Runs the Temporal worker that processes MVP workflow tasks.
"""

import asyncio
from temporalio.client import Client
from temporalio.worker import Worker
from config import settings
from workflows.mvp_workflow import MVPWorkflow
from workflows.activities import (
    analyze_idea_activity,
    generate_prd_activity,
    design_architecture_activity,
    create_agent_plan_activity,
    execute_agent_activity,
    review_outputs_activity,
    update_project_status_activity,
)
import structlog

logger = structlog.get_logger()


async def run_worker():
    """Start the Temporal worker."""
    logger.info(
        "starting_temporal_worker",
        host=settings.TEMPORAL_HOST,
        namespace=settings.TEMPORAL_NAMESPACE,
        task_queue=settings.TEMPORAL_TASK_QUEUE,
    )

    client = await Client.connect(
        settings.TEMPORAL_HOST,
        namespace=settings.TEMPORAL_NAMESPACE,
    )

    worker = Worker(
        client,
        task_queue=settings.TEMPORAL_TASK_QUEUE,
        workflows=[MVPWorkflow],
        activities=[
            analyze_idea_activity,
            generate_prd_activity,
            design_architecture_activity,
            create_agent_plan_activity,
            execute_agent_activity,
            review_outputs_activity,
            update_project_status_activity,
        ],
    )

    logger.info("temporal_worker_started", task_queue=settings.TEMPORAL_TASK_QUEUE)
    await worker.run()


if __name__ == "__main__":
    asyncio.run(run_worker())
