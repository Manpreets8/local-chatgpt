from functools import lru_cache
from pathlib import Path

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Project root is three levels up from this file (core -> app -> backend -> root).
_PROJECT_ROOT = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    """Central app configuration, loaded from environment variables / .env."""

    model_config = SettingsConfigDict(
        env_file=str(_PROJECT_ROOT / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_env: str = "development"
    app_secret_key: str = "change-me"

    anthropic_api_key: str = ""
    anthropic_model: str = "claude-sonnet-5"

    database_url: str = "postgresql://chatbot:change-me@localhost:5432/personal_ai_agent"

    jwt_secret_key: str = "change-me"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 60

    cors_origins: str = "http://localhost:5173"

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @model_validator(mode="after")
    def _strip_string_values(self) -> "Settings":
        # Env vars pasted through a dashboard UI (Render, etc.) can pick up
        # a stray trailing newline or spaces, which breaks things like HTTP
        # headers built from an API key in a way that's hard to spot by eye.
        for name in self.model_fields:
            value = getattr(self, name)
            if isinstance(value, str):
                setattr(self, name, value.strip())
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
