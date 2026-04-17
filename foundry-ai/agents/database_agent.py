"""
Foundry AI — Database Agent
Generates the database schema and data contract (schema.json).
This agent runs FIRST — all other agents depend on its output.
"""

import json
from typing import Any, Dict, Optional
from agents.base import BaseAgent


DATABASE_AGENT_SYSTEM = """You are the Database Agent for Foundry AI.
Your job is to generate a complete database schema based on the architecture and PRD.

You produce the DATA CONTRACT (schema.json) that ALL other agents must comply with.

RULES:
- Generate a complete, normalized database schema
- Include all entities, fields, types, constraints, and relationships
- Use standard SQL types: uuid, varchar, text, integer, float, boolean, timestamp, jsonb
- Every entity must have: id (uuid, PK), created_at (timestamp), updated_at (timestamp)
- Define all foreign key relationships
- Include indexes for common query patterns
- Output as structured JSON"""

DATABASE_AGENT_USER = """Generate a complete database schema for this project:

PRD:
{prd}

ARCHITECTURE:
{architecture}

Return a JSON object with this structure:
{{
    "project_name": "name",
    "schema_version": "1.0.0",
    "entities": [
        {{
            "name": "EntityName",
            "table_name": "entity_names",
            "description": "What this entity represents",
            "fields": [
                {{
                    "name": "field_name",
                    "type": "uuid|varchar|text|integer|float|boolean|timestamp|jsonb",
                    "primary_key": false,
                    "nullable": true,
                    "unique": false,
                    "default": null,
                    "description": "Field description",
                    "max_length": null,
                    "foreign_key": null
                }}
            ],
            "relationships": [
                {{"type": "has_many|belongs_to|has_one|many_to_many", "entity": "OtherEntity", "foreign_key": "field_name"}}
            ],
            "indexes": [
                {{"fields": ["field1", "field2"], "unique": false}}
            ]
        }}
    ],
    "enums": [
        {{"name": "StatusEnum", "values": ["active", "inactive"]}}
    ],
    "sql_migrations": [
        "CREATE TABLE ... SQL statement"
    ]
}}

Return ONLY valid JSON."""


class DatabaseAgent(BaseAgent):
    """
    Database Agent — generates schema.json (the data contract).
    Runs first in the pipeline. All other agents depend on this output.
    """

    agent_type = "DatabaseAgent"
    description = "Generates database schema and data contract"
    default_model = "claude-sonnet-4-20250514"

    async def execute(
        self,
        task: dict,
        prd: dict,
        architecture: dict,
        schema_contract: Optional[dict] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        task_name = task.get("task", "generate_schema")
        await self.notify_start(task_name)

        try:
            user_prompt = DATABASE_AGENT_USER.format(
                prd=json.dumps(prd, indent=2, default=str),
                architecture=json.dumps(architecture, indent=2, default=str),
            )

            schema = await self._generate(
                system_prompt=DATABASE_AGENT_SYSTEM,
                user_prompt=user_prompt,
            )

            await self.notify_complete(task_name)

            return {
                "schema": schema,
                "files": {
                    "schemas/schema.json": json.dumps(schema, indent=2),
                },
            }

        except Exception as e:
            await self.notify_error(task_name, str(e))
            return {"error": str(e)}
