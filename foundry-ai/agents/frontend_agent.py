"""
Foundry AI — Frontend Agent
Generates Next.js + React + Tailwind frontend code.
Must connect to backend APIs and comply with the data contract.
"""

import json
from typing import Any, Dict, Optional
from agents.base import BaseAgent


FRONTEND_AGENT_SYSTEM = """You are the Frontend Agent for Foundry AI.
Your job is to generate a complete Next.js frontend with React and Tailwind CSS.

RULES:
- Generate production-quality TypeScript/React code
- Use Next.js App Router (app/ directory)
- Use Tailwind CSS for styling
- Create a modern, responsive, premium-looking UI
- Connect to the backend API endpoints
- Include proper loading states and error handling
- Use dark theme with glassmorphism effects
- Output as structured JSON with file paths and code content"""

FRONTEND_AGENT_USER = """Generate a complete Next.js frontend:

PRD:
{prd}

ARCHITECTURE:
{architecture}

DATA CONTRACT:
{schema}

BACKEND API SUMMARY:
{api_summary}

TASK DETAILS:
{task}

Return a JSON object:
{{
    "files": {{
        "frontend/src/app/layout.tsx": "root layout code",
        "frontend/src/app/page.tsx": "home page code",
        "frontend/src/app/globals.css": "global styles with tailwind",
        "frontend/src/components/ComponentName.tsx": "component code",
        "frontend/src/lib/api.ts": "API client",
        "frontend/src/lib/types.ts": "TypeScript types matching schema",
        "frontend/package.json": "dependencies",
        "frontend/tailwind.config.ts": "tailwind configuration"
    }},
    "pages": ["list of pages created"],
    "components": ["list of components created"],
    "notes": "Any implementation notes"
}}

Return ONLY valid JSON. Code must be complete and runnable."""


class FrontendAgent(BaseAgent):
    """
    Frontend Agent — generates Next.js + React + Tailwind UI.
    Depends on DatabaseAgent (data contract) and BackendAgent (API endpoints).
    """

    agent_type = "FrontendAgent"
    description = "Builds UI using Next.js, React, and Tailwind"
    default_model = "gpt-4o"

    async def execute(
        self,
        task: dict,
        prd: dict,
        architecture: dict,
        schema_contract: Optional[dict] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        task_name = task.get("task", "build_frontend")
        await self.notify_start(task_name)

        try:
            # Get backend API summary if available
            backend_output = kwargs.get("backend_output", {})
            api_summary = json.dumps(
                backend_output.get("api_summary", []),
                indent=2,
                default=str,
            )

            user_prompt = FRONTEND_AGENT_USER.format(
                prd=json.dumps(prd, indent=2, default=str),
                architecture=json.dumps(architecture, indent=2, default=str),
                schema=json.dumps(schema_contract or {}, indent=2, default=str),
                api_summary=api_summary,
                task=json.dumps(task, indent=2, default=str),
            )

            result = await self._generate(
                system_prompt=FRONTEND_AGENT_SYSTEM,
                user_prompt=user_prompt,
                max_tokens=12000,
            )

            await self.notify_complete(task_name)
            return result

        except Exception as e:
            await self.notify_error(task_name, str(e))
            return {"error": str(e)}
