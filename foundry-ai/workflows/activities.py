"""
Foundry AI — Temporal Activities
Each activity wraps a council or agent operation for durable execution.
Activities are retried automatically by Temporal on failure.
"""

import json
from dataclasses import dataclass
from temporalio import activity
from typing import Dict, Any
import structlog

logger = structlog.get_logger()


@dataclass
class CouncilInput:
    project_id: str
    idea: str
    context: str  # JSON string of additional context


@dataclass
class AgentInput:
    project_id: str
    task: str  # JSON string of task definition
    prd: str  # JSON string
    architecture: str  # JSON string
    schema_contract: str  # JSON string
    extra_context: str  # JSON string of additional kwargs


# ─── Council Activities ───────────────────────────────────

@activity.defn
async def analyze_idea_activity(input: CouncilInput) -> str:
    """Council analyzes the user's idea. All 4 models run in parallel."""
    from council.engine import CouncilEngine

    council = CouncilEngine(input.project_id)
    analyses = await council.analyze_idea(input.idea)

    return json.dumps(analyses, default=str)


@activity.defn
async def generate_prd_activity(input: CouncilInput) -> str:
    """GPT generates the PRD based on council analyses."""
    from council.engine import CouncilEngine

    council = CouncilEngine(input.project_id)
    context = json.loads(input.context)
    analyses = context.get("analyses", {})

    prd = await council.generate_prd(input.idea, analyses)

    return json.dumps(prd, default=str)


@activity.defn
async def design_architecture_activity(input: CouncilInput) -> str:
    """Claude designs the system architecture."""
    from council.engine import CouncilEngine

    council = CouncilEngine(input.project_id)
    context = json.loads(input.context)
    prd = context.get("prd", {})

    architecture = await council.design_architecture(input.idea, prd)

    return json.dumps(architecture, default=str)


@activity.defn
async def create_agent_plan_activity(input: CouncilInput) -> str:
    """GPT creates the agent task plan."""
    from council.engine import CouncilEngine

    council = CouncilEngine(input.project_id)
    context = json.loads(input.context)
    prd = context.get("prd", {})
    architecture = context.get("architecture", {})

    plan = await council.create_agent_plan(input.idea, prd, architecture)

    return json.dumps(plan, default=str)


@activity.defn
async def review_outputs_activity(input: CouncilInput) -> str:
    """Groq performs fast QA review of agent outputs."""
    from council.engine import CouncilEngine

    council = CouncilEngine(input.project_id)
    context = json.loads(input.context)

    review = await council.review_outputs(context.get("agent_outputs", {}))

    return json.dumps(review, default=str)


# ─── Agent Activities ─────────────────────────────────────

@activity.defn
async def execute_agent_activity(input: AgentInput) -> str:
    """Execute a single agent task."""
    from agents.registry import get_agent

    task = json.loads(input.task)
    prd = json.loads(input.prd)
    architecture = json.loads(input.architecture)
    schema_contract = json.loads(input.schema_contract) if input.schema_contract else None
    extra = json.loads(input.extra_context) if input.extra_context else {}

    agent_type = task.get("assigned_agent", "")
    agent = get_agent(agent_type, input.project_id)

    result = await agent.execute(
        task=task,
        prd=prd,
        architecture=architecture,
        schema_contract=schema_contract,
        **extra,
    )

    return json.dumps(result, default=str)


# ─── Database Activities ──────────────────────────────────

@activity.defn
async def update_project_status_activity(input: CouncilInput) -> str:
    """Update project status in the database."""
    from database import async_session
    from models import Project
    from sqlalchemy import select

    context = json.loads(input.context)
    new_status = context.get("status", "")

    async with async_session() as session:
        result = await session.execute(
            select(Project).where(Project.id == input.project_id)
        )
        project = result.scalar_one()
        project.status = new_status

        # Update optional fields
        if "prd" in context:
            project.prd = context["prd"]
        if "architecture" in context:
            project.architecture = context["architecture"]
        if "agent_plan" in context:
            project.agent_plan = context["agent_plan"]
        if "schema_contract" in context:
            project.schema_contract = context["schema_contract"]
        if "final_output" in context:
            project.final_output = context["final_output"]
        if "project_structure" in context:
            project.project_structure = context["project_structure"]

        await session.commit()

    return json.dumps({"status": "updated"})
