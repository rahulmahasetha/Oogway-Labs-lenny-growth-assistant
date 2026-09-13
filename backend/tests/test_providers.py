"""Tests for LLM provider abstraction."""

import pytest
from unittest.mock import patch, MagicMock

from app.services.llm.base import LLMProvider
from app.services.llm.factory import get_llm_provider, reset_provider
from app.utils.errors import ProviderError


def test_provider_interface_is_abstract():
    """LLMProvider should not be instantiable directly."""
    with pytest.raises(TypeError):
        LLMProvider()


def test_factory_creates_ollama_provider():
    """Factory should create OllamaProvider when configured."""
    reset_provider()
    with patch("app.services.llm.factory.settings") as mock_settings:
        mock_settings.llm_provider = "ollama"
        mock_settings.ollama_base_url = "http://localhost:11434"
        mock_settings.ollama_model = "llama3.2"
        provider = get_llm_provider()
        assert provider.provider_name == "ollama"
        assert provider.model_name == "llama3.2"
    reset_provider()


def test_factory_rejects_unknown_provider():
    """Factory should raise ProviderError for unknown providers."""
    reset_provider()
    with patch("app.services.llm.factory.settings") as mock_settings:
        mock_settings.llm_provider = "nonexistent"
        with pytest.raises(ProviderError):
            get_llm_provider()
    reset_provider()


def test_factory_openai_requires_api_key():
    """Factory should raise ProviderError when OpenAI key is missing."""
    reset_provider()
    with patch("app.services.llm.factory.settings") as mock_settings:
        mock_settings.llm_provider = "openai"
        mock_settings.openai_api_key = None
        mock_settings.openai_model = "gpt-4o-mini"
        with pytest.raises(ProviderError) as exc_info:
            get_llm_provider()
        assert "OPENAI_API_KEY" in str(exc_info.value.detail)
    reset_provider()


def test_factory_anthropic_requires_api_key():
    """Factory should raise ProviderError when Anthropic key is missing."""
    reset_provider()
    with patch("app.services.llm.factory.settings") as mock_settings:
        mock_settings.llm_provider = "anthropic"
        mock_settings.anthropic_api_key = None
        mock_settings.anthropic_model = "claude-sonnet-4-20250514"
        with pytest.raises(ProviderError) as exc_info:
            get_llm_provider()
        assert "ANTHROPIC_API_KEY" in str(exc_info.value.detail)
    reset_provider()


def test_factory_singleton_behavior():
    """Factory should return the same instance on subsequent calls."""
    reset_provider()
    with patch("app.services.llm.factory.settings") as mock_settings:
        mock_settings.llm_provider = "ollama"
        mock_settings.ollama_base_url = "http://localhost:11434"
        mock_settings.ollama_model = "llama3.2"
        p1 = get_llm_provider()
        p2 = get_llm_provider()
        assert p1 is p2
    reset_provider()


def test_factory_reset():
    """reset_provider should clear the singleton."""
    reset_provider()
    with patch("app.services.llm.factory.settings") as mock_settings:
        mock_settings.llm_provider = "ollama"
        mock_settings.ollama_base_url = "http://localhost:11434"
        mock_settings.ollama_model = "llama3.2"
        p1 = get_llm_provider()
        reset_provider()
        p2 = get_llm_provider()
        assert p1 is not p2
    reset_provider()
