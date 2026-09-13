"""Anthropic LLM provider."""

from anthropic import AsyncAnthropic

from app.config import settings
from app.services.llm.base import LLMProvider
from app.utils.errors import ProviderError
from app.utils.logging import get_logger

logger = get_logger("anthropic_provider")


class AnthropicProvider(LLMProvider):
    """Anthropic API provider (Claude models)."""

    def __init__(self):
        if not settings.anthropic_api_key:
            raise ProviderError(
                "anthropic",
                "ANTHROPIC_API_KEY is not set. Add it to your .env file.",
            )
        self._client = AsyncAnthropic(api_key=settings.anthropic_api_key)
        self._model = settings.anthropic_model

    @property
    def provider_name(self) -> str:
        return "anthropic"

    @property
    def model_name(self) -> str:
        return self._model

    async def generate(
        self,
        system_prompt: str,
        messages: list[dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> str:
        """Generate response via Anthropic API."""
        try:
            response = await self._client.messages.create(
                model=self._model,
                system=system_prompt,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return response.content[0].text

        except httpx.RequestError as e:
            raise ProviderError("anthropic", f"Network error: {e!s}")
        except Exception as e:
            error_msg = str(e)
            if "api_key" in error_msg.lower() or "authentication" in error_msg.lower():
                raise ProviderError(
                    "anthropic", "Invalid API key. Check your ANTHROPIC_API_KEY."
                )
            raise ProviderError("anthropic", f"API error: {error_msg[:200]}")
