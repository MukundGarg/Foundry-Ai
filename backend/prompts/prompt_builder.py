"""
Prompt builder — generates optimized prompts for each task using the LLM itself.
"""

import json
from services.base import BaseAIService, CompletionRequest
from prompts.system_prompts import PROMPT_GENERATOR_SYSTEM
from utils.text import extract_json
from utils.logger import get_logger

logger = get_logger(__name__)


async def generate_task_prompt(
    task: dict,
    project_context: dict,
    service: BaseAIService,
) -> dict:
    """
    Use the AI to generate an optimized prompt for a specific task.
    Returns {"system_prompt": str, "user_prompt": str}
    """
    user_content = f"""Project Context:
{json.dumps(project_context, indent=2)}

Task to generate prompt for:
{json.dumps(task, indent=2)}

Generate an optimized prompt for a {task.get('agent_type', 'general')} agent to complete this task."""

    response = await service.complete(
        CompletionRequest(
            system_prompt=PROMPT_GENERATOR_SYSTEM,
            user_prompt=user_content,
            temperature=0.4,
            max_tokens=1024,
        )
    )

    try:
        return extract_json(response.content)
    except ValueError:
        logger.warning(f"Could not parse prompt JSON for task {task.get('id')}, using fallback")
        return {
            "system_prompt": f"You are an expert {task.get('agent_type', 'AI')} agent.",
            "user_prompt": task.get("description", ""),
        }
