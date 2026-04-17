"""
Foundry AI — Configuration
Loads environment variables and provides typed settings.
"""

from pydantic_settings import BaseSettings
from typing import List
import json


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # --- LLM API Keys ---
    ANTHROPIC_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    GOOGLE_API_KEY: str = ""
    GROQ_API_KEY: str = ""

    # --- Database ---
    DATABASE_URL: str = "postgresql+asyncpg://foundry:foundry@localhost:5432/foundry_ai"

    # --- Temporal ---
    TEMPORAL_HOST: str = "localhost:7233"
    TEMPORAL_NAMESPACE: str = "foundry-ai"
    TEMPORAL_TASK_QUEUE: str = "foundry-mvp-queue"

    # --- Backend ---
    BACKEND_HOST: str = "0.0.0.0"
    BACKEND_PORT: int = 8000
    CORS_ORIGINS: str = '["http://localhost:3000"]'

    # --- General ---
    LOG_LEVEL: str = "INFO"
    ENV: str = "development"

    @property
    def cors_origins_list(self) -> List[str]:
        return json.loads(self.CORS_ORIGINS)

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
