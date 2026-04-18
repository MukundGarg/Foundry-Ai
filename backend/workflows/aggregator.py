"""
Result Aggregator — combines all agent outputs into a final coherent result.
"""

import json
from services.base import BaseAIService, CompletionRequest
from agents.base_agent import AgentResult
from prompts.system_prompts import RESULT_AGGREGATOR_SYSTEM
from utils.logger import get_logger

logger = get_logger(__name__)


async def aggregate_results(
    project: dict,
    tasks: list[dict],
    results: list[AgentResult],
    service: BaseAIService,
) -> str:
    """
    Synthesize all task outputs into a final deliverable.
    Returns a markdown-formatted string.
    """
    logger.info("Aggregating results...")

    # Build a structured summary of all outputs
    outputs_summary = []
    for result in results:
        task = next((t for t in tasks if t["id"] == result.task_id), {})
        outputs_summary.append({
            "task_id": result.task_id,
            "task_title": task.get("title", result.task_id),
            "agent_type": result.agent_type,
            "success": result.success,
            "output": result.output if result.success else f"FAILED: {result.error}",
        })

    user_prompt = f"""Project: {project.get('title', 'Unknown')}
Goal: {project.get('goal', '')}

Task Outputs:
{json.dumps(outputs_summary, indent=2)}

Synthesize all outputs into a comprehensive final result document."""

    response = await service.complete(
        CompletionRequest(
            system_prompt=RESULT_AGGREGATOR_SYSTEM,
            user_prompt=user_prompt,
            temperature=0.5,
            max_tokens=4096,
        )
    )

    return response.content
