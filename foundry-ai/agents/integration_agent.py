"""
Foundry AI — Integration Agent
Connects all generated components, validates schema compliance,
and resolves integration issues. Assembles the final MVP.
"""

import json
from typing import Any, Dict, Optional
from agents.base import BaseAgent


INTEGRATION_AGENT_SYSTEM = """You are the Integration Agent for Foundry AI.
Your job is to:
1. Validate that all generated code complies with the data contract (schema.json)
2. Identify integration issues between components
3. Generate any glue code needed to connect components
4. Produce the final project structure

RULES:
- Check that backend models match schema.json entities
- Check that frontend types match the API contract
- Identify missing connections or incompatible interfaces
- Generate integration fixes as needed
- Produce a final directory tree of the complete project
- Output as structured JSON"""

INTEGRATION_AGENT_USER = """Validate and integrate the following components:

DATA CONTRACT:
{schema}

BACKEND OUTPUT:
{backend_output}

FRONTEND OUTPUT:
{frontend_output}

DEVOPS OUTPUT:
{devops_output}

REVIEW NOTES:
{review}

Return a JSON object:
{{
    "schema_compliance": {{
        "backend_models_match": true,
        "frontend_types_match": true,
        "api_contract_valid": true,
        "issues": []
    }},
    "integration_fixes": {{
        "files": {{
            "path/to/fix.ext": "fixed code content"
        }}
    }},
    "project_structure": {{
        "name": "project-name",
        "directories": [
            {{
                "path": "backend/",
                "files": ["main.py", "models.py", "..."]
            }}
        ]
    }},
    "setup_instructions": [
        "Step 1: ...",
        "Step 2: ..."
    ],
    "ready_for_deployment": true,
    "notes": "Any integration notes"
}}

Return ONLY valid JSON."""


class IntegrationAgent(BaseAgent):
    """
    Integration Agent — validates compliance and assembles the MVP.
    Runs after Backend, Frontend, and DevOps agents.
    """

    agent_type = "IntegrationAgent"
    description = "Connects components and validates schema compliance"
    default_model = "gpt-4o"

    async def execute(
        self,
        task: dict,
        prd: dict,
        architecture: dict,
        schema_contract: Optional[dict] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        task_name = task.get("task", "integrate_components")
        await self.notify_start(task_name)

        try:
            user_prompt = INTEGRATION_AGENT_USER.format(
                schema=json.dumps(schema_contract or {}, indent=2, default=str),
                backend_output=json.dumps(
                    kwargs.get("backend_output", {}), indent=2, default=str
                )[:8000],
                frontend_output=json.dumps(
                    kwargs.get("frontend_output", {}), indent=2, default=str
                )[:8000],
                devops_output=json.dumps(
                    kwargs.get("devops_output", {}), indent=2, default=str
                )[:5000],
                review=json.dumps(
                    kwargs.get("review", {}), indent=2, default=str
                ),
            )

            result = await self._generate(
                system_prompt=INTEGRATION_AGENT_SYSTEM,
                user_prompt=user_prompt,
                max_tokens=8000,
            )

            await self.notify_complete(task_name)
            return result

        except Exception as e:
            await self.notify_error(task_name, str(e))
            return {"error": str(e)}

    async def assemble_mvp(
        self,
        prd: dict,
        architecture: dict,
        agent_outputs: Dict[str, Any],
        review: dict,
    ) -> Dict[str, Any]:
        """
        Final MVP assembly — combines all outputs and validates.
        """
        await self.notify_start("assemble_mvp")

        try:
            task = {"task": "assemble_mvp", "description": "Final integration and assembly"}

            result = await self.execute(
                task=task,
                prd=prd,
                architecture=architecture,
                schema_contract=agent_outputs.get("schema"),
                backend_output=agent_outputs.get("backend", {}),
                frontend_output=agent_outputs.get("frontend", {}),
                devops_output=agent_outputs.get("devops", {}),
                review=review,
            )

            # Merge all generated files into final output
            all_files = {}
            for agent_key, output in agent_outputs.items():
                if isinstance(output, dict) and "files" in output:
                    all_files.update(output["files"])

            # Add integration fixes
            if isinstance(result, dict) and "integration_fixes" in result:
                fixes = result["integration_fixes"]
                if isinstance(fixes, dict) and "files" in fixes:
                    all_files.update(fixes["files"])

            result["all_files"] = all_files
            result["prd"] = prd
            result["architecture"] = architecture

            await self.notify_complete("assemble_mvp")
            return result

        except Exception as e:
            await self.notify_error("assemble_mvp", str(e))
            return {"error": str(e)}
