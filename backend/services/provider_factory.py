"""
Provider factory — resolves which AI service to use based on available keys
and an optional preferred provider.
"""

from typing import Optional
from config import settings
from services.base import BaseAIService
from services.openai_service import OpenAIService
from services.anthropic_service import AnthropicService
from services.google_service import GoogleService
from services.groq_service import GroqService
from utils.logger import get_logger

logger = get_logger(__name__)

# Priority order when no preference is given
PROVIDER_PRIORITY = ["openai", "anthropic", "google", "groq"]


def build_services(api_keys: dict[str, str]) -> dict[str, BaseAIService]:
    """
    Build a map of provider_name -> service instance from the given keys.
    Falls back to server-side env keys if a user key is not provided.
    """
    resolved: dict[str, str] = {
        "openai": api_keys.get("openai") or settings.openai_api_key,
        "anthropic": api_keys.get("anthropic") or settings.anthropic_api_key,
        "google": api_keys.get("google") or settings.google_api_key,
        "groq": api_keys.get("groq") or settings.groq_api_key,
    }

    services: dict[str, BaseAIService] = {
        "openai": OpenAIService(resolved["openai"]),
        "anthropic": AnthropicService(resolved["anthropic"]),
        "google": GoogleService(resolved["google"]),
        "groq": GroqService(resolved["groq"]),
    }

    available = [name for name, svc in services.items() if svc.is_available()]
    logger.info(f"Available providers: {available}")
    return services


def select_provider(
    services: dict[str, BaseAIService],
    preferred: Optional[str] = None,
) -> BaseAIService:
    """
    Return the best available provider service.
    Respects the preferred provider if it's available, otherwise falls back
    through the priority list.
    """
    if preferred and preferred in services and services[preferred].is_available():
        return services[preferred]

    for name in PROVIDER_PRIORITY:
        if name in services and services[name].is_available():
            logger.info(f"Selected provider: {name}")
            return services[name]

    raise ValueError(
        "No AI provider is available. Please configure at least one API key."
    )
