"""Config endpoint — exposes active provider/model to the frontend."""

from fastapi import APIRouter

from app.config import settings
from app.schemas import AppConfig

router = APIRouter()


def _get_active_model() -> str:
    """Return the model name for the active provider."""
    if settings.llm_provider == "ollama":
        return settings.ollama_model
    elif settings.llm_provider == "openai":
        return settings.openai_model
    elif settings.llm_provider == "anthropic":
        return settings.anthropic_model
    return "unknown"


@router.get("/config", response_model=AppConfig)
async def get_config():
    """Get the active application configuration."""
    return AppConfig(
        llm_provider=settings.llm_provider,
        llm_model=_get_active_model(),
        embedding_model=settings.embedding_model,
        rag_top_k=settings.rag_top_k,
        rag_similarity_threshold=settings.rag_similarity_threshold,
    )
