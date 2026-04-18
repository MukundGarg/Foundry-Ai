"""
Abstract base class for all AI provider adapters.
Every provider must implement `complete()`.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass
class CompletionRequest:
    system_prompt: str
    user_prompt: str
    temperature: float = 0.7
    max_tokens: int = 4096
    model: Optional[str] = None  # Override default model if needed


@dataclass
class CompletionResponse:
    content: str
    provider: str
    model: str
    input_tokens: int
    output_tokens: int


class BaseAIService(ABC):
    provider_name: str = ""
    default_model: str = ""

    @abstractmethod
    async def complete(self, request: CompletionRequest) -> CompletionResponse:
        """Send a prompt and return the completion."""
        ...

    @abstractmethod
    def is_available(self) -> bool:
        """Return True if the provider has a valid API key configured."""
        ...
