"""
Foundry AI — Base Agent
Abstract base class for all execution agents.
Agents generate code and infrastructure — they do NOT make architectural decisions.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import json
import litellm
from ws_manager import manager
import structlog

logger = structlog.get_logger()

litellm.suppress_debug_info = True


def _parse_json_response(text: str) -> dict:
    """Parse JSON from LLM response, handling markdown code blocks."""
    text = text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        lines = [l for l in lines if not l.strip().startswith("```")]
        text = "\n".join(lines)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}") + 1
        if start != -1 and end > start:
            try:
                return json.loads(text[start:end])
            except json.JSONDecodeError:
                pass
        return {"raw_response": text, "parse_error": True}


class BaseAgent(ABC):
    """
    Base execution agent.
    
    All agents:
    - Receive structured task assignments from the council
    - Generate code, configs, or infrastructure artifacts
    - Must comply with the data contract (schema.json)
    - Cannot redesign architecture
    """

    agent_type: str = "BaseAgent"
    description: str = "Base execution agent"
    default_model: str = "gpt-4o"  # Default model for code generation

    def __init__(self, project_id: str):
        self.project_id = project_id

    async def _generate(
        self,
        system_prompt: str,
        user_prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: int = 8000,
    ) -> dict:
        """Call LLM via LiteLLM for code generation."""
        model = model or self.default_model

        try:
            logger.info(
                "agent_generating",
                agent=self.agent_type,
                model=model,
            )

            response = await litellm.acompletion(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=temperature,
                max_tokens=max_tokens,
            )

            content = response.choices[0].message.content
            result = _parse_json_response(content)

            await manager.send_event(self.project_id, "agent_progress", {
                "agent": self.agent_type,
                "status": "generated",
            })

            return result

        except Exception as e:
            logger.error("agent_generation_error", agent=self.agent_type, error=str(e))
            return {"error": str(e), "agent": self.agent_type}

    @abstractmethod
    async def execute(
        self,
        task: dict,
        prd: dict,
        architecture: dict,
        schema_contract: Optional[dict] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Execute the assigned task.
        
        Args:
            task: The task assignment from the council
            prd: Product Requirements Document
            architecture: System architecture plan
            schema_contract: Data contract from DatabaseAgent (None for DatabaseAgent itself)
        
        Returns:
            Dict of generated artifacts (file paths → content)
        """
        ...

    async def notify_start(self, task_name: str):
        """Notify that this agent has started execution."""
        await manager.send_event(self.project_id, "agent_started", {
            "agent": self.agent_type,
            "task": task_name,
        })
        await manager.send_log(
            self.project_id,
            self.agent_type,
            f"🤖 {self.agent_type} started: {task_name}",
        )

    async def notify_complete(self, task_name: str):
        """Notify that this agent has completed execution."""
        await manager.send_event(self.project_id, "agent_completed", {
            "agent": self.agent_type,
            "task": task_name,
        })
        await manager.send_log(
            self.project_id,
            self.agent_type,
            f"✅ {self.agent_type} completed: {task_name}",
        )

    async def notify_error(self, task_name: str, error: str):
        """Notify that this agent encountered an error."""
        await manager.send_event(self.project_id, "agent_failed", {
            "agent": self.agent_type,
            "task": task_name,
            "error": error,
        })
        await manager.send_log(
            self.project_id,
            self.agent_type,
            f"❌ {self.agent_type} failed: {error}",
            level="error",
        )
