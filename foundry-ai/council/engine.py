"""
Foundry AI — Council Engine
Orchestrates multi-model deliberation through LiteLLM.
The council analyzes ideas, generates PRDs, designs architecture,
and creates agent task plans — it NEVER generates code.
"""

import asyncio
import json
import litellm
from typing import Dict, Any, Optional
from council.prompts import (
    COUNCIL_ROLES,
    IDEA_ANALYSIS_SYSTEM, IDEA_ANALYSIS_USER,
    PRD_SYSTEM, PRD_USER,
    ARCHITECTURE_SYSTEM, ARCHITECTURE_USER,
    AGENT_PLAN_SYSTEM, AGENT_PLAN_USER,
    REVIEW_SYSTEM, REVIEW_USER,
)
from ws_manager import manager
import structlog

logger = structlog.get_logger()

# Suppress LiteLLM noise
litellm.suppress_debug_info = True


def _parse_json_response(text: str) -> dict:
    """Parse JSON from LLM response, handling markdown code blocks."""
    text = text.strip()
    # Strip markdown code blocks if present
    if text.startswith("```"):
        lines = text.split("\n")
        # Remove first and last lines (```json and ```)
        lines = [l for l in lines if not l.strip().startswith("```")]
        text = "\n".join(lines)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Try to extract JSON from the text
        start = text.find("{")
        end = text.rfind("}") + 1
        if start != -1 and end > start:
            try:
                return json.loads(text[start:end])
            except json.JSONDecodeError:
                pass
        logger.warning("json_parse_failed", text=text[:200])
        return {"raw_response": text, "parse_error": True}


class CouncilEngine:
    """
    AI Council Engine — orchestrates multi-model deliberation.
    
    Each council member has a specific role:
    - Claude: Chief Architect (system design)
    - GPT: Product Strategist (product planning)
    - Gemini: Research Analyst (validation)
    - Groq: QA Evaluator (fast checks)
    """

    def __init__(self, project_id: str):
        self.project_id = project_id
        self.roles = COUNCIL_ROLES

    def get_role(self, model_name: str) -> str:
        """Get the council role for a model."""
        return self.roles.get(model_name, {}).get("role", "Unknown")

    async def _call_model(self, model_key: str, system_prompt: str, user_prompt: str) -> dict:
        """Call a single model via LiteLLM and parse JSON response."""
        role_info = self.roles[model_key]
        model = role_info["model"]

        try:
            logger.info("council_calling_model", model=model_key, model_id=model)

            response = await litellm.acompletion(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.7,
                max_tokens=4000,
                response_format={"type": "json_object"},
            )

            content = response.choices[0].message.content
            result = _parse_json_response(content)

            logger.info("council_model_responded", model=model_key, keys=list(result.keys()) if isinstance(result, dict) else "non-dict")

            return result

        except Exception as e:
            logger.error("council_model_error", model=model_key, error=str(e))
            return {
                "error": str(e),
                "model": model_key,
                "fallback": True,
            }

    async def analyze_idea(self, idea: str) -> Dict[str, dict]:
        """
        Phase 1: All council members analyze the idea in parallel.
        Returns dict mapping model_key → analysis result.
        """
        await manager.send_event(self.project_id, "council_started", {"phase": "idea_analysis"})

        tasks = {}
        for model_key, role_info in self.roles.items():
            system = IDEA_ANALYSIS_SYSTEM.format(
                role_name=role_info["name"],
                role_title=role_info["role"],
                responsibility=role_info["responsibility"],
            )
            user = IDEA_ANALYSIS_USER.format(
                role_title=role_info["role"],
                idea=idea,
            )
            tasks[model_key] = self._call_model(model_key, system, user)

        # Execute all analyses in parallel
        results = await asyncio.gather(*tasks.values(), return_exceptions=True)

        analyses = {}
        for model_key, result in zip(tasks.keys(), results):
            if isinstance(result, Exception):
                analyses[model_key] = {"error": str(result), "fallback": True}
            else:
                analyses[model_key] = result

            await manager.send_event(self.project_id, "council_analysis", {
                "model": model_key,
                "role": self.get_role(model_key),
                "complete": True,
            })

        return analyses

    async def generate_prd(self, idea: str, analyses: Dict[str, dict]) -> dict:
        """
        Phase 2: GPT (Product Strategist) generates the PRD using all analyses.
        """
        await manager.send_event(self.project_id, "council_started", {"phase": "prd_generation"})

        analyses_text = json.dumps(analyses, indent=2, default=str)
        user_prompt = PRD_USER.format(idea=idea, analyses=analyses_text)

        prd = await self._call_model("gpt", PRD_SYSTEM, user_prompt)

        await manager.send_event(self.project_id, "council_prd", {"prd": prd})
        return prd

    async def design_architecture(self, idea: str, prd: dict) -> dict:
        """
        Phase 3: Claude (Chief Architect) designs the system architecture.
        """
        await manager.send_event(self.project_id, "council_started", {"phase": "architecture"})

        prd_text = json.dumps(prd, indent=2, default=str)
        user_prompt = ARCHITECTURE_USER.format(idea=idea, prd=prd_text)

        architecture = await self._call_model("claude", ARCHITECTURE_SYSTEM, user_prompt)

        await manager.send_event(self.project_id, "council_architecture", {"architecture": architecture})
        return architecture

    async def create_agent_plan(self, idea: str, prd: dict, architecture: dict) -> dict:
        """
        Phase 4: GPT creates the agent task plan.
        """
        await manager.send_event(self.project_id, "council_started", {"phase": "agent_planning"})

        prd_text = json.dumps(prd, indent=2, default=str)
        arch_text = json.dumps(architecture, indent=2, default=str)
        user_prompt = AGENT_PLAN_USER.format(
            idea=idea, prd=prd_text, architecture=arch_text
        )

        plan = await self._call_model("gpt", AGENT_PLAN_SYSTEM, user_prompt)

        await manager.send_event(self.project_id, "council_agent_plan", {"agent_plan": plan})
        return plan

    async def review_outputs(self, agent_outputs: Dict[str, Any]) -> dict:
        """
        Phase 5: Groq (QA Evaluator) performs fast validation of agent outputs.
        """
        await manager.send_event(self.project_id, "review_started", {})

        outputs_text = json.dumps(agent_outputs, indent=2, default=str)
        # Truncate if too long for fast eval
        if len(outputs_text) > 15000:
            outputs_text = outputs_text[:15000] + "\n... (truncated)"

        user_prompt = REVIEW_USER.format(outputs=outputs_text)

        review = await self._call_model("groq", REVIEW_SYSTEM, user_prompt)

        await manager.send_event(self.project_id, "review_complete", {"review": review})
        return review
