"""
Workflow Executor — runs tasks respecting dependency order.

Tasks with no dependencies (parallel_safe=True and no deps) run concurrently.
Tasks with dependencies run after their prerequisites complete.
"""

import asyncio
from typing import Optional
from services.base import BaseAIService
from agents.registry import get_agent
from agents.base_agent import AgentResult
from prompts.prompt_builder import generate_task_prompt
from utils.logger import get_logger

logger = get_logger(__name__)


async def execute_task(
    task: dict,
    project: dict,
    service: BaseAIService,
    completed_results: dict[str, AgentResult],
) -> AgentResult:
    """Execute a single task, injecting context from completed dependencies."""
    # Build context from dependency outputs
    dep_context = ""
    for dep_id in task.get("dependencies", []):
        if dep_id in completed_results and completed_results[dep_id].success:
            dep_context += f"\n\n--- Output from {dep_id} ---\n{completed_results[dep_id].output}"

    # Generate optimized prompts for this task
    prompts = await generate_task_prompt(task, project, service)

    # Inject dependency context into user prompt
    user_prompt = prompts["user_prompt"]
    if dep_context:
        user_prompt = f"{user_prompt}\n\nContext from previous tasks:{dep_context}"

    agent = get_agent(task.get("agent_type", "researcher"), service)
    return await agent.execute(
        task=task,
        system_prompt=prompts["system_prompt"],
        user_prompt=user_prompt,
    )


async def execute_workflow(
    tasks: list[dict],
    project: dict,
    service: BaseAIService,
) -> list[AgentResult]:
    """
    Execute all tasks in dependency order.
    Independent tasks run in parallel; dependent tasks wait for prerequisites.
    """
    completed: dict[str, AgentResult] = {}
    results: list[AgentResult] = []
    pending = {task["id"]: task for task in tasks}

    max_rounds = len(tasks) + 1  # Safety limit
    round_num = 0

    while pending and round_num < max_rounds:
        round_num += 1

        # Find tasks whose dependencies are all satisfied
        ready = [
            task
            for task in pending.values()
            if all(dep in completed for dep in task.get("dependencies", []))
        ]

        if not ready:
            # Circular dependency or unresolvable — run remaining tasks anyway
            logger.warning("Possible circular dependency detected, running remaining tasks")
            ready = list(pending.values())

        logger.info(f"Round {round_num}: executing {len(ready)} task(s) in parallel")

        # Run ready tasks concurrently
        round_results = await asyncio.gather(
            *[
                execute_task(task, project, service, completed)
                for task in ready
            ],
            return_exceptions=False,
        )

        for result in round_results:
            completed[result.task_id] = result
            results.append(result)
            pending.pop(result.task_id, None)

    return results
