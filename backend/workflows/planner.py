"""
Workflow Planner — interprets the user idea and produces a structured task plan.

Pipeline:
  1. IdeaInterpreter  → structured project description
  2. TaskPlanner      → list of tasks with types and dependencies
  3. AgentRouter      → assigns agent_type to each task
"""

import json
from services.base import BaseAIService, CompletionRequest
from prompts.system_prompts import (
    IDEA_INTERPRETER_SYSTEM,
    TASK_PLANNER_SYSTEM,
    AGENT_ROUTER_SYSTEM,
)
from utils.text import extract_json
from utils.logger import get_logger

logger = get_logger(__name__)


async def interpret_idea(idea: str, service: BaseAIService) -> dict:
    """Step 1: Convert raw idea into structured project description."""
    logger.info("Interpreting idea...")
    response = await service.complete(
        CompletionRequest(
            system_prompt=IDEA_INTERPRETER_SYSTEM,
            user_prompt=f"Project idea: {idea}",
            temperature=0.3,
            max_tokens=1024,
        )
    )
    logger.info(f"Idea interpreter raw response (first 200 chars): {response.content[:200]}")
    return extract_json(response.content)


async def plan_tasks(project: dict, service: BaseAIService) -> list[dict]:
    """Step 2: Break the project into concrete tasks."""
    logger.info("Planning tasks...")
    response = await service.complete(
        CompletionRequest(
            system_prompt=TASK_PLANNER_SYSTEM,
            user_prompt=f"Project description:\n{json.dumps(project, indent=2)}",
            temperature=0.3,
            max_tokens=2048,
        )
    )
    tasks = extract_json(response.content)
    if not isinstance(tasks, list):
        raise ValueError("Task planner did not return a list of tasks")
    return tasks


async def route_agents(tasks: list[dict], service: BaseAIService) -> list[dict]:
    """Step 3: Assign the best agent type to each task."""
    logger.info("Routing agents...")
    response = await service.complete(
        CompletionRequest(
            system_prompt=AGENT_ROUTER_SYSTEM,
            user_prompt=f"Tasks to route:\n{json.dumps(tasks, indent=2)}",
            temperature=0.2,
            max_tokens=2048,
        )
    )
    routed = extract_json(response.content)
    if not isinstance(routed, list):
        raise ValueError("Agent router did not return a list")
    return routed


async def build_plan(idea: str, service: BaseAIService) -> dict:
    """
    Full planning pipeline. Returns:
    {
      "project": {...},
      "tasks": [{...}],
    }
    """
    project = await interpret_idea(idea, service)
    tasks = await plan_tasks(project, service)
    routed_tasks = await route_agents(tasks, service)

    return {
        "project": project,
        "tasks": routed_tasks,
    }
