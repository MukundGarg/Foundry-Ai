"""
Foundry AI — Agent Dispatcher
Routes tasks to agents and manages execution order based on dependencies.
DatabaseAgent always runs first (produces the data contract).
"""

import asyncio
from typing import Any, Dict, List, Optional
from agents.registry import get_agent
from agents.base import BaseAgent
from ws_manager import manager
import structlog

logger = structlog.get_logger()


class AgentDispatcher:
    """
    Dispatches tasks to agents respecting dependency order.
    
    Execution order:
    1. DatabaseAgent (produces schema.json data contract)
    2. BackendAgent + FrontendAgent (can run in parallel, depend on schema)
    3. DevOpsAgent + IntegrationAgent (can run in parallel, depend on backend/frontend)
    """

    def __init__(self, project_id: str):
        self.project_id = project_id
        self.outputs: Dict[str, Any] = {}

    async def execute_all(
        self,
        tasks: List[dict],
        prd: dict,
        architecture: dict,
        schema_contract: Optional[dict],
        session=None,
        task_records: dict = None,
    ) -> Dict[str, Any]:
        """
        Execute all agent tasks in dependency order.
        
        Returns dict mapping output_key → result.
        """
        if not tasks:
            # Generate default task plan if none provided
            tasks = self._default_task_plan()

        await manager.send_event(self.project_id, "agents_dispatching", {
            "total_tasks": len(tasks),
        })

        # Group tasks by execution order
        execution_groups = self._resolve_execution_order(tasks)

        for group_idx, group in enumerate(execution_groups):
            logger.info(
                "executing_group",
                group=group_idx + 1,
                total_groups=len(execution_groups),
                tasks=[t.get("task") for t in group],
            )

            await manager.send_log(
                self.project_id,
                "dispatcher",
                f"📦 Executing batch {group_idx + 1}/{len(execution_groups)}: {[t.get('assigned_agent') for t in group]}",
            )

            # Execute tasks in this group in parallel
            coroutines = []
            for task in group:
                coroutines.append(
                    self._execute_single(task, prd, architecture, session, task_records)
                )

            results = await asyncio.gather(*coroutines, return_exceptions=True)

            # Collect results
            for task, result in zip(group, results):
                agent_type = task.get("assigned_agent", "")
                task_key = self._agent_to_key(agent_type)

                if isinstance(result, Exception):
                    logger.error("agent_failed", agent=agent_type, error=str(result))
                    self.outputs[task_key] = {"error": str(result)}
                else:
                    self.outputs[task_key] = result

                    # Update schema_contract if database agent produced it
                    if agent_type == "DatabaseAgent" and isinstance(result, dict):
                        self.outputs["schema"] = result.get("schema", result)

                # Update task record status
                if task_records and task.get("task") in task_records:
                    record = task_records[task.get("task")]
                    if isinstance(result, Exception) or (isinstance(result, dict) and "error" in result):
                        record.status = "failed"
                        record.error_message = str(result) if isinstance(result, Exception) else result.get("error")
                    else:
                        record.status = "completed"
                        record.output_data = result if isinstance(result, dict) else {"result": str(result)}
                    if session:
                        await session.flush()

        return self.outputs

    async def _execute_single(
        self,
        task: dict,
        prd: dict,
        architecture: dict,
        session=None,
        task_records: dict = None,
    ) -> Dict[str, Any]:
        """Execute a single agent task."""
        agent_type = task.get("assigned_agent", "")

        # Update task record to running
        if task_records and task.get("task") in task_records:
            record = task_records[task.get("task")]
            record.status = "running"
            if session:
                await session.flush()

        agent = get_agent(agent_type, self.project_id)

        # Determine schema contract
        schema_contract = self.outputs.get("schema")

        # Pass additional context based on available outputs
        kwargs = {}
        if "backend" in self.outputs:
            kwargs["backend_output"] = self.outputs["backend"]
        if "frontend" in self.outputs:
            kwargs["frontend_output"] = self.outputs["frontend"]
        if "devops" in self.outputs:
            kwargs["devops_output"] = self.outputs["devops"]

        return await agent.execute(
            task=task,
            prd=prd,
            architecture=architecture,
            schema_contract=schema_contract,
            **kwargs,
        )

    def _resolve_execution_order(self, tasks: List[dict]) -> List[List[dict]]:
        """
        Resolve tasks into ordered execution groups.
        Tasks in the same group can run in parallel.
        """
        # Default ordering based on agent type
        order_map = {
            "DatabaseAgent": 0,
            "BackendAgent": 1,
            "FrontendAgent": 1,
            "DevOpsAgent": 2,
            "IntegrationAgent": 3,
        }

        # Group by execution priority
        groups: Dict[int, List[dict]] = {}
        for task in tasks:
            agent = task.get("assigned_agent", "")
            priority = order_map.get(agent, 2)
            if priority not in groups:
                groups[priority] = []
            groups[priority].append(task)

        # Sort by priority and return as ordered list
        return [groups[k] for k in sorted(groups.keys())]

    def _default_task_plan(self) -> List[dict]:
        """Generate a default task plan if the council doesn't provide one."""
        return [
            {
                "task": "generate_schema",
                "assigned_agent": "DatabaseAgent",
                "description": "Generate database schema and data contract",
                "dependencies": [],
                "priority": 1,
            },
            {
                "task": "build_backend",
                "assigned_agent": "BackendAgent",
                "framework": "FastAPI",
                "description": "Generate FastAPI backend with models, routes, and services",
                "dependencies": ["generate_schema"],
                "priority": 2,
            },
            {
                "task": "build_frontend",
                "assigned_agent": "FrontendAgent",
                "framework": "Next.js",
                "description": "Generate Next.js frontend with React components and Tailwind styling",
                "dependencies": ["generate_schema"],
                "priority": 2,
            },
            {
                "task": "build_devops",
                "assigned_agent": "DevOpsAgent",
                "description": "Generate Docker configuration and deployment setup",
                "dependencies": ["build_backend", "build_frontend"],
                "priority": 3,
            },
            {
                "task": "integrate_components",
                "assigned_agent": "IntegrationAgent",
                "description": "Validate schema compliance and assemble final MVP",
                "dependencies": ["build_backend", "build_frontend", "build_devops"],
                "priority": 4,
            },
        ]

    def _agent_to_key(self, agent_type: str) -> str:
        """Convert agent type to output key."""
        return {
            "DatabaseAgent": "database",
            "BackendAgent": "backend",
            "FrontendAgent": "frontend",
            "DevOpsAgent": "devops",
            "IntegrationAgent": "integration",
        }.get(agent_type, agent_type.lower())
