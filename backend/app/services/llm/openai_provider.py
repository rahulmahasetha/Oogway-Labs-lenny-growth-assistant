"""OpenAI LLM provider."""

from openai import AsyncOpenAI

from app.config import settings
from app.services.llm.base import LLMProvider
from app.utils.errors import ProviderError
from app.utils.logging import get_logger

logger = get_logger("openai_provider")


class OpenAIProvider(LLMProvider):
    """OpenAI API provider (GPT-4o, GPT-4o-mini, etc.)."""

    def __init__(self):
        if not settings.openai_api_key:
            raise ProviderError(
                "openai",
                "OPENAI_API_KEY is not set. Add it to your .env file.",
            )
        self._client = AsyncOpenAI(api_key=settings.openai_api_key)
        self._model = settings.openai_model

    @property
    def provider_name(self) -> str:
        return "openai"

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
        """Generate response via OpenAI API."""
        openai_messages = [{"role": "system", "content": system_prompt}]
        openai_messages.extend(messages)

        try:
            response = await self._client.chat.completions.create(
                model=self._model,
                messages=openai_messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return response.choices[0].message.content

        except Exception as e:
            error_msg = str(e)
            if "api_key" in error_msg.lower() or "authentication" in error_msg.lower():
                raise ProviderError(
                    "openai", "Invalid API key. Check your OPENAI_API_KEY."
                )
            raise ProviderError("openai", f"API error: {error_msg[:200]}")

    async def generate_image(self, prompt: str) -> str | None:
        """Generate an image using DALL-E 3."""
        try:
            logger.info("generating_image", prompt=prompt[:80])
            response = await self._client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size="1024x1024",
                quality="standard",
                n=1,
            )
            return response.data[0].url
        except Exception as e:
            logger.error("image_generation_failed", error=str(e))
            return None
