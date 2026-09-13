"""Health check endpoint."""

import httpx
from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.schemas import HealthResponse
from app.utils.logging import get_logger

logger = get_logger("health")
router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check(db: AsyncSession = Depends(get_db)):
    """Check application health including database and Ollama connectivity."""
    # Check database
    db_status = "healthy"
    try:
        await db.execute(text("SELECT 1"))
    except Exception as e:
        logger.error("health_db_failure", error=str(e))
        db_status = f"unhealthy: {str(e)[:100]}"

    # Check Ollama
    ollama_status = "not configured"
    if settings.llm_provider == "ollama":
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(f"{settings.ollama_base_url}/api/tags")
                if resp.status_code == 200:
                    ollama_status = "healthy"
                else:
                    ollama_status = f"unhealthy: HTTP {resp.status_code}"
        except Exception as e:
            ollama_status = f"unavailable: {str(e)[:100]}"

    overall = "healthy" if db_status == "healthy" else "degraded"

    return HealthResponse(
        status=overall,
        database=db_status,
        ollama=ollama_status,
    )
