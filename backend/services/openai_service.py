from openai import AsyncOpenAI
from services.base import BaseAIService, CompletionRequest, CompletionResponse
from utils.logger import get_logger

logger = get_logger(__name__)


class OpenAIService(BaseAIService):
    provider_name = "openai"
    default_model = "gpt-4o"

    def __init__(self, api_key: str):
        self._api_key = api_key
        self._client = AsyncOpenAI(api_key=api_key) if api_key else None

    def is_available(self) -> bool:
        return bool(self._api_key)

    async def complete(self, request: CompletionRequest) -> CompletionResponse:
        if not self._client:
            raise ValueError("OpenAI API key not configured")

        model = request.model or self.default_model
        logger.info(f"[OpenAI] Calling model={model}")

        response = await self._client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": request.system_prompt},
                {"role": "user", "content": request.user_prompt},
            ],
            temperature=request.temperature,
            max_tokens=request.max_tokens,
        )

        choice = response.choices[0]
        return CompletionResponse(
            content=choice.message.content or "",
            provider=self.provider_name,
            model=model,
            input_tokens=response.usage.prompt_tokens if response.usage else 0,
            output_tokens=response.usage.completion_tokens if response.usage else 0,
        )
