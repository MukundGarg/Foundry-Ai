"""
Foundry AI — MVP Workflow
Temporal workflow definition for the full MVP generation pipeline.
Orchestrates council deliberation → agent execution → review → integration.
"""

import json
from datetime import timedelta
from temporalio import workflow
from temporalio.common import RetryPolicy

with workflow.unsafe.imports_passed_through():
    from workflows.activities import (
        CouncilInput,
        AgentInput,
        analyze_idea_activity,
        generate_prd_activity,
        design_architecture_activity,
        create_agent_plan_activity,
        execute_agent_activity,
        review_outputs_activity,
        update_project_status_activity,
    )


# Retry policy for LLM calls — allow retries for transient failures
LLM_RETRY_POLICY = RetryPolicy(
    initial_interval=timedelta(seconds=5),
    backoff_coefficient=2.0,
    maximum_interval=timedelta(minutes=2),
    maximum_attempts=3,
)

# Longer timeout for LLM operations
LLM_TIMEOUT = timedelta(minutes=5)


@workflow.defn
class MVPWorkflow:
    """
    Temporal workflow for generating an MVP from a user's idea.
    
    Phases:
    1. Council Analysis (parallel — all 4 models)
    2. PRD Generation (GPT)
    3. Architecture Design (Claude)
    4. Agent Task Planning (GPT)
    5. Database Agent (produces data contract)
    6. Backend + Frontend Agents (parallel)
    7. DevOps Agent
    8. Council Review (Groq — fast QA)
    9. Integration Agent (final assembly)
    """

    @workflow.run
    async def run(self, project_id: str, idea: str) -> str:
        """Execute the full MVP generation pipeline."""

        # ─── Phase 1: Council Analysis ───────────────────
        await workflow.execute_activity(
            update_project_status_activity,
            CouncilInput(
                project_id=project_id,
                idea=idea,
                context=json.dumps({"status": "council_analyzing"}),
            ),
            start_to_close_timeout=timedelta(seconds=30),
        )

        analyses_json = await workflow.execute_activity(
            analyze_idea_activity,
            CouncilInput(project_id=project_id, idea=idea, context="{}"),
            start_to_close_timeout=LLM_TIMEOUT,
            retry_policy=LLM_RETRY_POLICY,
        )
        analyses = json.loads(analyses_json)

        # ─── Phase 2: PRD Generation ─────────────────────
        prd_json = await workflow.execute_activity(
            generate_prd_activity,
            CouncilInput(
                project_id=project_id,
                idea=idea,
                context=json.dumps({"analyses": analyses}),
            ),
            start_to_close_timeout=LLM_TIMEOUT,
            retry_policy=LLM_RETRY_POLICY,
        )
        prd = json.loads(prd_json)

        # ─── Phase 3: Architecture Design ────────────────
        await workflow.execute_activity(
            update_project_status_activity,
            CouncilInput(
                project_id=project_id,
                idea=idea,
                context=json.dumps({"status": "council_planning", "prd": prd}),
            ),
            start_to_close_timeout=timedelta(seconds=30),
        )

        architecture_json = await workflow.execute_activity(
            design_architecture_activity,
            CouncilInput(
                project_id=project_id,
                idea=idea,
                context=json.dumps({"prd": prd}),
            ),
            start_to_close_timeout=LLM_TIMEOUT,
            retry_policy=LLM_RETRY_POLICY,
        )
        architecture = json.loads(architecture_json)

        # ─── Phase 4: Agent Task Planning ────────────────
        agent_plan_json = await workflow.execute_activity(
            create_agent_plan_activity,
            CouncilInput(
                project_id=project_id,
                idea=idea,
                context=json.dumps({"prd": prd, "architecture": architecture}),
            ),
            start_to_close_timeout=LLM_TIMEOUT,
            retry_policy=LLM_RETRY_POLICY,
        )
        agent_plan = json.loads(agent_plan_json)

        # Update project with architecture and plan
        await workflow.execute_activity(
            update_project_status_activity,
            CouncilInput(
                project_id=project_id,
                idea=idea,
                context=json.dumps({
                    "status": "agents_executing",
                    "architecture": architecture,
                    "agent_plan": agent_plan,
                }),
            ),
            start_to_close_timeout=timedelta(seconds=30),
        )

        # ─── Phase 5: Database Agent ─────────────────────
        db_task = {
            "task": "generate_schema",
            "assigned_agent": "DatabaseAgent",
            "description": "Generate database schema and data contract",
        }

        db_result_json = await workflow.execute_activity(
            execute_agent_activity,
            AgentInput(
                project_id=project_id,
                task=json.dumps(db_task),
                prd=json.dumps(prd),
                architecture=json.dumps(architecture),
                schema_contract="",
                extra_context="{}",
            ),
            start_to_close_timeout=LLM_TIMEOUT,
            retry_policy=LLM_RETRY_POLICY,
        )
        db_result = json.loads(db_result_json)
        schema_contract = db_result.get("schema", {})

        # Save schema contract
        await workflow.execute_activity(
            update_project_status_activity,
            CouncilInput(
                project_id=project_id,
                idea=idea,
                context=json.dumps({"schema_contract": schema_contract}),
            ),
            start_to_close_timeout=timedelta(seconds=30),
        )

        # ─── Phase 6: Backend + Frontend (parallel) ──────
        tasks = agent_plan.get("tasks", [])

        backend_task = next((t for t in tasks if t.get("assigned_agent") == "BackendAgent"), {
            "task": "build_backend",
            "assigned_agent": "BackendAgent",
            "framework": "FastAPI",
            "description": "Generate FastAPI backend",
        })

        frontend_task = next((t for t in tasks if t.get("assigned_agent") == "FrontendAgent"), {
            "task": "build_frontend",
            "assigned_agent": "FrontendAgent",
            "framework": "Next.js",
            "description": "Generate Next.js frontend",
        })

        # Run backend and frontend in parallel
        backend_future = workflow.execute_activity(
            execute_agent_activity,
            AgentInput(
                project_id=project_id,
                task=json.dumps(backend_task),
                prd=json.dumps(prd),
                architecture=json.dumps(architecture),
                schema_contract=json.dumps(schema_contract),
                extra_context="{}",
            ),
            start_to_close_timeout=timedelta(minutes=8),
            retry_policy=LLM_RETRY_POLICY,
        )

        frontend_future = workflow.execute_activity(
            execute_agent_activity,
            AgentInput(
                project_id=project_id,
                task=json.dumps(frontend_task),
                prd=json.dumps(prd),
                architecture=json.dumps(architecture),
                schema_contract=json.dumps(schema_contract),
                extra_context="{}",
            ),
            start_to_close_timeout=timedelta(minutes=8),
            retry_policy=LLM_RETRY_POLICY,
        )

        backend_result_json, frontend_result_json = await asyncio.gather(
            backend_future, frontend_future
        )

        backend_result = json.loads(backend_result_json)
        frontend_result = json.loads(frontend_result_json)

        # ─── Phase 7: DevOps Agent ───────────────────────
        devops_task = next((t for t in tasks if t.get("assigned_agent") == "DevOpsAgent"), {
            "task": "build_devops",
            "assigned_agent": "DevOpsAgent",
            "description": "Generate Docker configuration",
        })

        devops_result_json = await workflow.execute_activity(
            execute_agent_activity,
            AgentInput(
                project_id=project_id,
                task=json.dumps(devops_task),
                prd=json.dumps(prd),
                architecture=json.dumps(architecture),
                schema_contract=json.dumps(schema_contract),
                extra_context=json.dumps({
                    "project_structure": {
                        "backend": list(backend_result.get("files", {}).keys()),
                        "frontend": list(frontend_result.get("files", {}).keys()),
                    }
                }),
            ),
            start_to_close_timeout=LLM_TIMEOUT,
            retry_policy=LLM_RETRY_POLICY,
        )
        devops_result = json.loads(devops_result_json)

        # ─── Phase 8: Council Review ─────────────────────
        await workflow.execute_activity(
            update_project_status_activity,
            CouncilInput(
                project_id=project_id,
                idea=idea,
                context=json.dumps({"status": "review_in_progress"}),
            ),
            start_to_close_timeout=timedelta(seconds=30),
        )

        agent_outputs = {
            "database": db_result,
            "backend": backend_result,
            "frontend": frontend_result,
            "devops": devops_result,
            "schema": schema_contract,
        }

        review_json = await workflow.execute_activity(
            review_outputs_activity,
            CouncilInput(
                project_id=project_id,
                idea=idea,
                context=json.dumps({"agent_outputs": agent_outputs}),
            ),
            start_to_close_timeout=LLM_TIMEOUT,
            retry_policy=LLM_RETRY_POLICY,
        )
        review = json.loads(review_json)

        # ─── Phase 9: Integration ────────────────────────
        await workflow.execute_activity(
            update_project_status_activity,
            CouncilInput(
                project_id=project_id,
                idea=idea,
                context=json.dumps({"status": "integrating"}),
            ),
            start_to_close_timeout=timedelta(seconds=30),
        )

        integration_task = {
            "task": "integrate_components",
            "assigned_agent": "IntegrationAgent",
            "description": "Validate and integrate all components",
        }

        integration_result_json = await workflow.execute_activity(
            execute_agent_activity,
            AgentInput(
                project_id=project_id,
                task=json.dumps(integration_task),
                prd=json.dumps(prd),
                architecture=json.dumps(architecture),
                schema_contract=json.dumps(schema_contract),
                extra_context=json.dumps({
                    "backend_output": backend_result,
                    "frontend_output": frontend_result,
                    "devops_output": devops_result,
                    "review": review,
                }),
            ),
            start_to_close_timeout=LLM_TIMEOUT,
            retry_policy=LLM_RETRY_POLICY,
        )
        integration_result = json.loads(integration_result_json)

        # ─── Finalize ────────────────────────────────────
        final_output = {
            "prd": prd,
            "architecture": architecture,
            "schema": schema_contract,
            "agent_outputs": agent_outputs,
            "review": review,
            "integration": integration_result,
            "project_structure": integration_result.get("project_structure", {}),
        }

        await workflow.execute_activity(
            update_project_status_activity,
            CouncilInput(
                project_id=project_id,
                idea=idea,
                context=json.dumps({
                    "status": "completed",
                    "final_output": final_output,
                    "project_structure": integration_result.get("project_structure", {}),
                }),
            ),
            start_to_close_timeout=timedelta(seconds=30),
        )

        return json.dumps({"status": "completed", "project_id": project_id})
