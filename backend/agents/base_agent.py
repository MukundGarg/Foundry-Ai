"""
Base agent class. All specialized agents inherit from this.
"""

from dataclasses import dataclass, field
from typing import Optional
from services.base import BaseAIService, CompletionRequest
from utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class AgentResult:
    task_id: str
    agent_type: str
    output: str
    provider: str
    model: str
    input_tokens: int
    output_tokens: int
    success: bool
    error: Optional[str] = None
    metadata: dict = field(default_factory=dict)


class BaseAgent:
    agent_type: str = "base"

    def __init__(self, service: BaseAIService):
        self.service = service

    async def execute(
        self,
        task: dict,
        system_prompt: str,
        user_prompt: str,
    ) -> AgentResult:
        """Execute a task using the provided prompts."""
        logger.info(f"[{self.agent_type}] Executing task: {task.get('id')}")

        try:
            response = await self.service.complete(
                CompletionRequest(
                    system_prompt=system_prompt,
                    user_prompt=user_prompt,
                    temperature=self._get_temperature(),
                    max_tokens=self._get_max_tokens(),
                )
            )
            return AgentResult(
                task_id=task.get("id", "unknown"),
                agent_type=self.agent_type,
                output=response.content,
                provider=response.provider,
                model=response.model,
                input_tokens=response.input_tokens,
                output_tokens=response.output_tokens,
                success=True,
            )
        except Exception as e:
            logger.error(f"[{self.agent_type}] Task {task.get('id')} failed: {e}")
            return AgentResult(
                task_id=task.get("id", "unknown"),
                agent_type=self.agent_type,
                output="",
                provider=self.service.provider_name,
                model=self.service.default_model,
                input_tokens=0,
                output_tokens=0,
                success=False,
                error=str(e),
            )

    def _get_temperature(self) -> float:
        return 0.7

    def _get_max_tokens(self) -> int:
        return 4096
