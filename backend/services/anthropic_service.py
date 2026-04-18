import anthropic
from services.base import BaseAIService, CompletionRequest, CompletionResponse
from utils.logger import get_logger

logger = get_logger(__name__)


class AnthropicService(BaseAIService):
    provider_name = "anthropic"
    default_model = "claude-3-5-sonnet-20241022"

    def __init__(self, api_key: str):
        self._api_key = api_key
        self._client = anthropic.AsyncAnthropic(api_key=api_key) if api_key else None

    def is_available(self) -> bool:
        return bool(self._api_key)

    async def complete(self, request: CompletionRequest) -> CompletionResponse:
        if not self._client:
            raise ValueError("Anthropic API key not configured")

        model = request.model or self.default_model
        logger.info(f"[Anthropic] Calling model={model}")

        response = await self._client.messages.create(
            model=model,
            max_tokens=request.max_tokens,
            system=request.system_prompt,
            messages=[{"role": "user", "content": request.user_prompt}],
            temperature=request.temperature,
        )

        content = ""
        for block in response.content:
            if hasattr(block, "text"):
                content += block.text

        return CompletionResponse(
            content=content,
            provider=self.provider_name,
            model=model,
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens,
        )
