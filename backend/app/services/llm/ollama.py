"""Ollama LLM provider."""

import httpx

from app.config import settings
from app.services.llm.base import LLMProvider
from app.utils.errors import ProviderError
from app.utils.logging import get_logger

logger = get_logger("ollama")


class OllamaProvider(LLMProvider):
    """Local Ollama provider for running models like llama3.2."""

    def __init__(self):
        self._base_url = settings.ollama_base_url
        self._model = settings.ollama_model

    @property
    def provider_name(self) -> str:
        return "ollama"

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
        """Generate response via Ollama HTTP API."""
        # Build the message list with system prompt
        ollama_messages = [{"role": "system", "content": system_prompt}]
        ollama_messages.extend(messages)

        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    f"{self._base_url}/api/chat",
                    json={
                        "model": self._model,
                        "messages": ollama_messages,
                        "stream": False,
                        "options": {
                            "temperature": temperature,
                            "num_predict": max_tokens,
                        },
                    },
                )

                if response.status_code != 200:
                    raise ProviderError(
                        "ollama",
                        f"HTTP {response.status_code}: {response.text[:200]}",
                    )

                data = response.json()
                return data["message"]["content"]

        except httpx.ConnectError:
            raise ProviderError(
                "ollama",
                f"Cannot connect to Ollama at {self._base_url}. "
                "Is Ollama running? Start it with: ollama serve",
            )
        except httpx.TimeoutException:
            raise ProviderError(
                "ollama",
                "Request timed out. The model may be loading or the query too complex.",
            )
        except ProviderError:
            raise
        except Exception as e:
            raise ProviderError("ollama", f"Unexpected error: {e!s}")
