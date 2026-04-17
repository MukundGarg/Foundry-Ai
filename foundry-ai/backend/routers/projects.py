"""
Foundry AI — Ideas Router
Handles project idea submission and triggers the MVP pipeline.
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database import get_db
from models import Project, ProjectStatus
from schemas import IdeaSubmission, ProjectResponse, ProjectDetail, CouncilDecisionResponse, AgentTaskResponse
from ws_manager import manager
import structlog

logger = structlog.get_logger()

router = APIRouter(prefix="/api/projects", tags=["projects"])


@router.post("", response_model=ProjectResponse, status_code=201)
async def submit_idea(
    submission: IdeaSubmission,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """Submit a product idea to start the Foundry AI pipeline."""
    project = Project(idea=submission.idea, status=ProjectStatus.SUBMITTED.value)
    db.add(project)
    await db.flush()
    await db.refresh(project)

    project_id = project.id

    logger.info("project_created", project_id=project_id, idea_length=len(submission.idea))

    # Trigger the pipeline in the background
    background_tasks.add_task(start_pipeline, project_id, submission.idea)

    return ProjectResponse(
        id=project.id,
        idea=project.idea,
        status=project.status,
        created_at=project.created_at,
    )


@router.get("/{project_id}", response_model=ProjectDetail)
async def get_project(project_id: str, db: AsyncSession = Depends(get_db)):
    """Get full project details including council decisions and agent tasks."""
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Eagerly load relationships
    await db.refresh(project, ["council_decisions", "agent_tasks"])

    return ProjectDetail(
        id=project.id,
        idea=project.idea,
        status=project.status,
        prd=project.prd,
        architecture=project.architecture,
        schema_contract=project.schema_contract,
        agent_plan=project.agent_plan,
        project_structure=project.project_structure,
        council_decisions=[
            CouncilDecisionResponse(
                id=d.id,
                phase=d.phase,
                model_name=d.model_name,
                role=d.role,
                content=d.content,
                created_at=d.created_at,
            )
            for d in project.council_decisions
        ],
        agent_tasks=[
            AgentTaskResponse(
                id=t.id,
                agent_type=t.agent_type,
                task_name=t.task_name,
                description=t.description,
                status=t.status,
                output_data=t.output_data,
                error_message=t.error_message,
                retry_count=t.retry_count,
                created_at=t.created_at,
                updated_at=t.updated_at,
            )
            for t in project.agent_tasks
        ],
        created_at=project.created_at,
        updated_at=project.updated_at,
    )


@router.get("", response_model=list[ProjectResponse])
async def list_projects(db: AsyncSession = Depends(get_db)):
    """List all projects."""
    result = await db.execute(
        select(Project).order_by(Project.created_at.desc()).limit(50)
    )
    projects = result.scalars().all()
    return [
        ProjectResponse(
            id=p.id,
            idea=p.idea,
            status=p.status,
            created_at=p.created_at,
        )
        for p in projects
    ]


@router.get("/{project_id}/logs")
async def get_project_logs(project_id: str, db: AsyncSession = Depends(get_db)):
    """Get all logs for a project."""
    from models import ProjectLog
    from schemas import LogEntry

    result = await db.execute(
        select(ProjectLog)
        .where(ProjectLog.project_id == project_id)
        .order_by(ProjectLog.created_at.asc())
    )
    logs = result.scalars().all()
    return [
        LogEntry(
            id=log.id,
            source=log.source,
            level=log.level,
            message=log.message,
            metadata=log.metadata,
            created_at=log.created_at,
        )
        for log in logs
    ]


async def start_pipeline(project_id: str, idea: str):
    """
    Start the Foundry AI pipeline.
    In production this triggers a Temporal workflow.
    For MVP, runs the pipeline directly.
    """
    import asyncio
    from database import async_session
    from models import ProjectStatus

    try:
        # Try to connect to Temporal and start workflow
        from workflows.client import start_mvp_workflow
        await start_mvp_workflow(project_id, idea)
    except Exception as e:
        logger.warning("temporal_unavailable", error=str(e), fallback="direct_execution")

        # Fallback: run pipeline directly without Temporal
        from pipeline import run_pipeline_direct
        await run_pipeline_direct(project_id, idea)
