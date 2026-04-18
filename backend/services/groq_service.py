from groq import AsyncGroq
from services.base import BaseAIService, CompletionRequest, CompletionResponse
from utils.logger import get_logger

logger = get_logger(__name__)


class GroqService(BaseAIService):
    provider_name = "groq"
    default_model = "llama3-70b-8192"

    def __init__(self, api_key: str):
        self._api_key = api_key
        self._client = AsyncGroq(api_key=api_key) if api_key else None

    def is_available(self) -> bool:
        return bool(self._api_key)

    async def complete(self, request: CompletionRequest) -> CompletionResponse:
        if not self._client:
            raise ValueError("Groq API key not configured")

        model = request.model or self.default_model
        logger.info(f"[Groq] Calling model={model}")

        try:
            response = await self._client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": request.system_prompt},
                    {"role": "user", "content": request.user_prompt},
                ],
                temperature=request.temperature,
                max_tokens=request.max_tokens,
            )
        except Exception as e:
            logger.error(f"[Groq] API call failed: {e}", exc_info=True)
            raise

        choice = response.choices[0]
        logger.info(f"[Groq] Done. in={response.usage.prompt_tokens if response.usage else 0} out={response.usage.completion_tokens if response.usage else 0}")
        return CompletionResponse(
            content=choice.message.content or "",
            provider=self.provider_name,
            model=model,
            input_tokens=response.usage.prompt_tokens if response.usage else 0,
            output_tokens=response.usage.completion_tokens if response.usage else 0,
        )
