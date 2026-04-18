"""
Google Gemini service using the official google-genai SDK (v1+).
The old google-generativeai package is deprecated; this uses google.genai instead.
"""

import asyncio
from google import genai
from google.genai import types as genai_types
from services.base import BaseAIService, CompletionRequest, CompletionResponse
from utils.logger import get_logger

logger = get_logger(__name__)


class GoogleService(BaseAIService):
    provider_name = "google"
    default_model = "gemini-2.0-flash"

    def __init__(self, api_key: str):
        self._api_key = api_key
        self._client = genai.Client(api_key=api_key) if api_key else None

    def is_available(self) -> bool:
        return bool(self._api_key)

    async def complete(self, request: CompletionRequest) -> CompletionResponse:
        if not self._client:
            raise ValueError("Google API key not configured")

        model_name = request.model or self.default_model
        logger.info(f"[Google] Calling model={model_name}")

        config = genai_types.GenerateContentConfig(
            system_instruction=request.system_prompt,
            temperature=request.temperature,
            max_output_tokens=request.max_tokens,
        )

        def _sync_call() -> tuple[str, int, int]:
            response = self._client.models.generate_content(
                model=model_name,
                contents=request.user_prompt,
                config=config,
            )
            content = response.text or ""
            usage = response.usage_metadata
            input_tokens = usage.prompt_token_count if usage else 0
            output_tokens = usage.candidates_token_count if usage else 0
            return content, input_tokens, output_tokens

        try:
            content, input_tokens, output_tokens = await asyncio.to_thread(_sync_call)
        except Exception as e:
            logger.error(f"[Google] API call failed: {e}", exc_info=True)
            raise

        logger.info(f"[Google] Done. in={input_tokens} out={output_tokens}")
        return CompletionResponse(
            content=content,
            provider=self.provider_name,
            model=model_name,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
        )
