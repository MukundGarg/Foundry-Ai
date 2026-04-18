from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List


class Settings(BaseSettings):
    app_env: str = Field(default="development", alias="APP_ENV")
    app_host: str = Field(default="0.0.0.0", alias="APP_HOST")
    app_port: int = Field(default=8000, alias="APP_PORT")

    # Stored as a raw comma-separated string so pydantic-settings doesn't
    # try to JSON-decode it. Parsed into a list via the property below.
    cors_origins_raw: str = Field(
        default="http://localhost:3000", alias="CORS_ORIGINS"
    )

    # Workers for gunicorn (production). 0 = auto (2 * CPU + 1)
    workers: int = Field(default=1, alias="WORKERS")

    # Server-side fallback API keys (optional — users can supply via UI)
    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")
    anthropic_api_key: str = Field(default="", alias="ANTHROPIC_API_KEY")
    google_api_key: str = Field(default="", alias="GOOGLE_API_KEY")
    groq_api_key: str = Field(default="", alias="GROQ_API_KEY")

    @property
    def cors_origins(self) -> List[str]:
        """Parse CORS_ORIGINS from a comma-separated string."""
        return [o.strip() for o in self.cors_origins_raw.split(",") if o.strip()]

    model_config = {"env_file": ".env", "populate_by_name": True}


settings = Settings()
