"""
Foundry AI — Backend Agent
Generates FastAPI backend code: API routes, services, models, and configuration.
Must comply with the data contract from DatabaseAgent.
"""

import json
from typing import Any, Dict, Optional
from agents.base import BaseAgent


BACKEND_AGENT_SYSTEM = """You are the Backend Agent for Foundry AI.
Your job is to generate a complete FastAPI backend based on the architecture, PRD, and data contract.

RULES:
- Generate production-quality Python/FastAPI code
- You MUST comply with the provided data contract (schema.json)
- Include: main.py, models.py, schemas.py, routes, services
- Use async/await for all database operations
- Include proper error handling and validation
- Use Pydantic for request/response schemas
- Include CORS middleware setup
- Output as structured JSON with file paths and code content"""

BACKEND_AGENT_USER = """Generate a complete FastAPI backend:

PRD:
{prd}

ARCHITECTURE:
{architecture}

DATA CONTRACT (schema.json):
{schema}

TASK DETAILS:
{task}

Return a JSON object:
{{
    "files": {{
        "backend/main.py": "full python code content",
        "backend/models.py": "SQLAlchemy models matching schema.json",
        "backend/schemas.py": "Pydantic request/response schemas",
        "backend/database.py": "database connection setup",
        "backend/routes/resource_name.py": "API route handlers",
        "backend/services/service_name.py": "business logic",
        "backend/requirements.txt": "python dependencies"
    }},
    "api_summary": [
        {{"method": "GET", "path": "/api/...", "description": "..."}}
    ],
    "notes": "Any implementation notes"
}}

Return ONLY valid JSON. Code must be complete and runnable."""


class BackendAgent(BaseAgent):
    """
    Backend Agent — generates FastAPI backend code.
    Depends on DatabaseAgent for the data contract.
    """

    agent_type = "BackendAgent"
    description = "Builds APIs and services using FastAPI"
    default_model = "gpt-4o"

    async def execute(
        self,
        task: dict,
        prd: dict,
        architecture: dict,
        schema_contract: Optional[dict] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        task_name = task.get("task", "build_backend")
        await self.notify_start(task_name)

        try:
            user_prompt = BACKEND_AGENT_USER.format(
                prd=json.dumps(prd, indent=2, default=str),
                architecture=json.dumps(architecture, indent=2, default=str),
                schema=json.dumps(schema_contract or {}, indent=2, default=str),
                task=json.dumps(task, indent=2, default=str),
            )

            result = await self._generate(
                system_prompt=BACKEND_AGENT_SYSTEM,
                user_prompt=user_prompt,
                max_tokens=12000,
            )

            await self.notify_complete(task_name)
            return result

        except Exception as e:
            await self.notify_error(task_name, str(e))
            return {"error": str(e)}
