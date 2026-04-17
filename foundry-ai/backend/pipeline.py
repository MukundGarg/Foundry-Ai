"""
Foundry AI — Direct Pipeline Runner
Fallback pipeline execution when Temporal is unavailable.
Runs the full council → agents → integration pipeline in-process.
"""

import asyncio
import traceback
from database import async_session
from models import Project, ProjectStatus, ProjectLog, CouncilDecision, AgentTask, AgentTaskStatus
from ws_manager import manager
import structlog

logger = structlog.get_logger()


async def add_log(session, project_id: str, source: str, message: str, level: str = "info", metadata: dict = None):
    """Add a log entry and broadcast via WebSocket."""
    log = ProjectLog(
        project_id=project_id,
        source=source,
        level=level,
        message=message,
        metadata=metadata,
    )
    session.add(log)
    await session.flush()
    await manager.send_log(project_id, source, message, level)


async def update_status(session, project: Project, status: ProjectStatus):
    """Update project status and notify via WebSocket."""
    project.status = status.value
    await session.flush()
    await manager.send_event(project.id, "status_change", {"status": status.value})


async def run_pipeline_direct(project_id: str, idea: str):
    """
    Execute the full Foundry AI pipeline directly (no Temporal).
    
    Flow:
    1. Council analyzes idea
    2. Council generates PRD
    3. Council designs architecture
    4. Council creates agent task plan
    5. Database Agent generates schema (data contract)
    6. Backend Agent builds APIs
    7. Frontend Agent builds UI
    8. DevOps Agent creates infrastructure
    9. Integration Agent validates & assembles
    """
    async with async_session() as session:
        try:
            # Fetch project
            from sqlalchemy import select
            result = await session.execute(select(Project).where(Project.id == project_id))
            project = result.scalar_one()

            # ─── Phase 1: Council Analysis ───────────────────
            await update_status(session, project, ProjectStatus.COUNCIL_ANALYZING)
            await add_log(session, project_id, "council", "🧠 AI Council convened — analyzing idea...")

            from council.engine import CouncilEngine
            council = CouncilEngine(project_id)

            # 1a. Analyze the idea
            await manager.send_event(project_id, "council_started", {"phase": "analysis"})
            analyses = await council.analyze_idea(idea)

            for model_name, analysis in analyses.items():
                decision = CouncilDecision(
                    project_id=project_id,
                    phase="idea_analysis",
                    model_name=model_name,
                    role=council.get_role(model_name),
                    content=analysis,
                )
                session.add(decision)
                await manager.send_event(project_id, "council_analysis", {
                    "model": model_name,
                    "role": council.get_role(model_name),
                    "analysis": analysis,
                })

            await add_log(session, project_id, "council", "✅ Idea analysis complete from all council members")

            # 1b. Generate PRD
            await add_log(session, project_id, "council", "📋 Generating Product Requirements Document...")
            prd = await council.generate_prd(idea, analyses)
            project.prd = prd
            await session.flush()
            await manager.send_event(project_id, "council_prd", {"prd": prd})
            await add_log(session, project_id, "council", "✅ PRD generated")

            # ─── Phase 2: Architecture Planning ──────────────
            await update_status(session, project, ProjectStatus.COUNCIL_PLANNING)
            await add_log(session, project_id, "council", "🏗️ Designing system architecture...")

            architecture = await council.design_architecture(idea, prd)
            project.architecture = architecture

            arch_decision = CouncilDecision(
                project_id=project_id,
                phase="architecture",
                model_name="claude",
                role="Architecture Lead",
                content=architecture,
            )
            session.add(arch_decision)
            await session.flush()
            await manager.send_event(project_id, "council_architecture", {"architecture": architecture})
            await add_log(session, project_id, "council", "✅ Architecture plan finalized")

            # 1c. Create agent task plan
            await add_log(session, project_id, "council", "📝 Creating agent task plan...")
            agent_plan = await council.create_agent_plan(idea, prd, architecture)
            project.agent_plan = agent_plan
            await session.flush()
            await manager.send_event(project_id, "council_agent_plan", {"agent_plan": agent_plan})
            await add_log(session, project_id, "council", "✅ Agent task plan created")

            # ─── Phase 3: Agent Execution ────────────────────
            await update_status(session, project, ProjectStatus.AGENTS_EXECUTING)
            await add_log(session, project_id, "agents", "🤖 Dispatching execution agents...")

            from agents.dispatcher import AgentDispatcher
            dispatcher = AgentDispatcher(project_id)

            # Create agent task records
            task_records = {}
            tasks = agent_plan.get("tasks", [])
            for task_def in tasks:
                task_record = AgentTask(
                    project_id=project_id,
                    agent_type=task_def.get("assigned_agent", "Unknown"),
                    task_name=task_def.get("task", "Unknown Task"),
                    description=task_def.get("description", ""),
                    input_data=task_def,
                    depends_on=task_def.get("dependencies", []),
                )
                session.add(task_record)
                await session.flush()
                task_records[task_def.get("task", "")] = task_record

            # Execute agents in dependency order
            agent_outputs = await dispatcher.execute_all(
                tasks=tasks,
                prd=prd,
                architecture=architecture,
                schema_contract=None,  # Will be set after DatabaseAgent
                session=session,
                task_records=task_records,
            )

            # Store schema contract if generated
            if "schema" in agent_outputs:
                project.schema_contract = agent_outputs["schema"]
                await session.flush()

            await add_log(session, project_id, "agents", "✅ All agents completed execution")

            # ─── Phase 4: Review & Integration ───────────────
            await update_status(session, project, ProjectStatus.REVIEW_IN_PROGRESS)
            await add_log(session, project_id, "council", "🔍 Council reviewing agent outputs...")

            # Quick validation via Groq
            review_result = await council.review_outputs(agent_outputs)
            await manager.send_event(project_id, "review_complete", {"review": review_result})
            await add_log(session, project_id, "council", "✅ Review complete")

            # ─── Phase 5: Integration ────────────────────────
            await update_status(session, project, ProjectStatus.INTEGRATING)
            await add_log(session, project_id, "integration", "🔧 Assembling final MVP...")

            from agents.integration_agent import IntegrationAgent
            integrator = IntegrationAgent(project_id)
            final_output = await integrator.assemble_mvp(
                prd=prd,
                architecture=architecture,
                agent_outputs=agent_outputs,
                review=review_result,
            )

            project.final_output = final_output
            project.project_structure = final_output.get("project_structure", {})
            await update_status(session, project, ProjectStatus.COMPLETED)
            await session.commit()

            await manager.send_event(project_id, "project_completed", {
                "project_structure": final_output.get("project_structure", {}),
            })
            await add_log(session, project_id, "system", "🎉 MVP generation complete!")

        except Exception as e:
            logger.error("pipeline_failed", project_id=project_id, error=str(e))
            traceback.print_exc()

            try:
                project.status = ProjectStatus.FAILED.value
                await session.commit()
            except Exception:
                pass

            await manager.send_event(project_id, "project_failed", {"error": str(e)})
            await add_log(session, project_id, "system", f"❌ Pipeline failed: {str(e)}", level="error")
