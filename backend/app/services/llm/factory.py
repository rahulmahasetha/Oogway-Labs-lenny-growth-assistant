"""LLM provider factory — selects the active provider based on configuration."""

from app.config import settings
from app.services.llm.anthropic_provider import AnthropicProvider
from app.services.llm.base import LLMProvider
from app.services.llm.ollama import OllamaProvider
from app.services.llm.openai_provider import OpenAIProvider
from app.utils.errors import ProviderError
from app.utils.logging import get_logger

logger = get_logger("llm_factory")

# Singleton cache
_provider: LLMProvider | None = None


def get_llm_provider() -> LLMProvider:
    """
    Get the configured LLM provider.

    Returns a singleton instance based on the LLM_PROVIDER env var.
    Raises ProviderError if the provider is unknown or misconfigured.
    """
    global _provider

    if _provider is not None:
        return _provider

    provider_name = settings.llm_provider.lower()
    logger.info("initializing_llm_provider", provider=provider_name)

    if provider_name == "ollama":
        _provider = OllamaProvider()
    elif provider_name == "openai":
        _provider = OpenAIProvider()
    elif provider_name == "anthropic":
        _provider = AnthropicProvider()
    else:
        raise ProviderError(
            provider_name,
            f"Unknown LLM provider '{provider_name}'. "
            "Supported: ollama, openai, anthropic",
        )

    logger.info(
        "llm_provider_ready",
        provider=_provider.provider_name,
        model=_provider.model_name,
    )
    return _provider


def reset_provider() -> None:
    """Reset the provider singleton (for testing)."""
    global _provider
    _provider = None
