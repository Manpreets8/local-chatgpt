from anthropic import Anthropic, APIError

from app.core.config import get_settings


class LLMNotConfiguredError(Exception):
    """Raised when no usable Anthropic API key is configured."""


class LLMService:
    """Thin wrapper around the Anthropic client so the rest of the app
    never talks to the SDK directly. Keeping this in one place means we
    can add retries, swap models, or support another provider later
    without touching the API layer."""

    def __init__(self) -> None:
        self._client: Anthropic | None = None

    def _get_client(self) -> Anthropic:
        settings = get_settings()
        if not settings.anthropic_api_key or settings.anthropic_api_key.startswith("your-"):
            raise LLMNotConfiguredError(
                "ANTHROPIC_API_KEY is not set. Add a real key to your .env file."
            )
        if self._client is None:
            self._client = Anthropic(api_key=settings.anthropic_api_key)
        return self._client

    def chat(self, message: str) -> str:
        settings = get_settings()
        client = self._get_client()
        response = client.messages.create(
            model=settings.anthropic_model,
            max_tokens=1024,
            messages=[{"role": "user", "content": message}],
        )
        return response.content[0].text


llm_service = LLMService()

__all__ = ["llm_service", "LLMService", "LLMNotConfiguredError", "APIError"]
