"""
WorkflowEngine — the top-level orchestrator.

Ties together: planner → executor → aggregator
and returns a complete workflow result.
"""

import time
from dataclasses import dataclass, field
from typing import Optional

from services.provider_factory import build_services, select_provider
from workflows.planner import build_plan
from workflows.executor import execute_workflow
from workflows.aggregator import aggregate_results
from agents.base_agent import AgentResult
from utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class TaskSummary:
    id: str
    title: str
    type: str
    agent_type: str
    dependencies: list[str]
    parallel_safe: bool
    success: bool
    output_preview: str  # First 300 chars of output
    provider: str
    model: str
    input_tokens: int
    output_tokens: int
    error: Optional[str] = None


@dataclass
class WorkflowResult:
    idea: str
    project: dict
    tasks: list[TaskSummary]
    final_result: str
    total_input_tokens: int
    total_output_tokens: int
    provider_used: str
    duration_seconds: float
    success: bool
    error: Optional[str] = None


class WorkflowEngine:
    def __init__(self, api_keys: dict[str, str]):
        self.services = build_services(api_keys)

    async def plan(
        self,
        idea: str,
        preferred_provider: Optional[str] = None,
    ) -> dict:
        """Return the workflow plan without executing tasks."""
        service = select_provider(self.services, preferred_provider)
        plan = await build_plan(idea, service)
        return {
            "idea": idea,
            "project": plan["project"],
            "tasks": plan["tasks"],
            "provider": service.provider_name,
        }

    async def run(
        self,
        idea: str,
        preferred_provider: Optional[str] = None,
    ) -> dict:
        """Full pipeline: plan → execute → aggregate → return result."""
        start = time.time()
        service = select_provider(self.services, preferred_provider)
        logger.info(f"Starting workflow for: '{idea}' using {service.provider_name}")

        # Phase 1: Plan
        plan = await build_plan(idea, service)
        project = plan["project"]
        tasks = plan["tasks"]
        logger.info(f"Plan ready: {len(tasks)} tasks for '{project.get('title')}'")

        # Phase 2: Execute
        results: list[AgentResult] = await execute_workflow(tasks, project, service)

        # Phase 3: Aggregate
        final_result = await aggregate_results(project, tasks, results, service)

        # Build response
        duration = round(time.time() - start, 2)
        total_in = sum(r.input_tokens for r in results)
        total_out = sum(r.output_tokens for r in results)

        task_summaries = []
        for result in results:
            task = next((t for t in tasks if t["id"] == result.task_id), {})
            task_summaries.append({
                "id": result.task_id,
                "title": task.get("title", result.task_id),
                "type": task.get("type", ""),
                "agent_type": result.agent_type,
                "dependencies": task.get("dependencies", []),
                "parallel_safe": task.get("parallel_safe", False),
                "success": result.success,
                "output": result.output,
                "output_preview": result.output[:300] if result.output else "",
                "provider": result.provider,
                "model": result.model,
                "input_tokens": result.input_tokens,
                "output_tokens": result.output_tokens,
                "error": result.error,
            })

        return {
            "idea": idea,
            "project": project,
            "tasks": task_summaries,
            "final_result": final_result,
            "stats": {
                "total_input_tokens": total_in,
                "total_output_tokens": total_out,
                "provider_used": service.provider_name,
                "duration_seconds": duration,
                "tasks_completed": sum(1 for r in results if r.success),
                "tasks_failed": sum(1 for r in results if not r.success),
            },
            "success": True,
        }
