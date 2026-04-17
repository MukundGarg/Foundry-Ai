"""
Foundry AI — DevOps Agent
Generates Docker setup, CI/CD configuration, and deployment files.
"""

import json
from typing import Any, Dict, Optional
from agents.base import BaseAgent


DEVOPS_AGENT_SYSTEM = """You are the DevOps Agent for Foundry AI.
Your job is to generate Docker setup, deployment configuration, and CI/CD files.

RULES:
- Generate production-ready Docker configurations
- Create multi-stage Dockerfiles for optimal image size
- Include docker-compose.yml for local development
- Add health checks to all services
- Include environment variable templates
- Generate proper .dockerignore files
- Output as structured JSON with file paths and content"""

DEVOPS_AGENT_USER = """Generate Docker and deployment configuration:

ARCHITECTURE:
{architecture}

PROJECT STRUCTURE:
{project_structure}

TASK DETAILS:
{task}

Return a JSON object:
{{
    "files": {{
        "Dockerfile.backend": "multi-stage Dockerfile for FastAPI backend",
        "Dockerfile.frontend": "multi-stage Dockerfile for Next.js frontend",
        "docker-compose.yml": "compose file with all services",
        "docker-compose.dev.yml": "development overrides",
        ".dockerignore": "docker ignore rules",
        ".env.docker": "env template for Docker",
        "scripts/start.sh": "startup script"
    }},
    "services": ["list of services defined"],
    "ports": {{"service": "port_mapping"}},
    "notes": "Deployment notes"
}}

Return ONLY valid JSON."""


class DevOpsAgent(BaseAgent):
    """
    DevOps Agent — generates Docker and deployment configuration.
    Can run in parallel with IntegrationAgent.
    """

    agent_type = "DevOpsAgent"
    description = "Creates Docker setup and deployment configuration"
    default_model = "gpt-4o"

    async def execute(
        self,
        task: dict,
        prd: dict,
        architecture: dict,
        schema_contract: Optional[dict] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        task_name = task.get("task", "build_devops")
        await self.notify_start(task_name)

        try:
            project_structure = kwargs.get("project_structure", {})

            user_prompt = DEVOPS_AGENT_USER.format(
                architecture=json.dumps(architecture, indent=2, default=str),
                project_structure=json.dumps(project_structure, indent=2, default=str),
                task=json.dumps(task, indent=2, default=str),
            )

            result = await self._generate(
                system_prompt=DEVOPS_AGENT_SYSTEM,
                user_prompt=user_prompt,
                max_tokens=6000,
            )

            await self.notify_complete(task_name)
            return result

        except Exception as e:
            await self.notify_error(task_name, str(e))
            return {"error": str(e)}
