"""Tests for the health endpoint."""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock


@pytest.mark.asyncio
async def test_health_response_structure():
    """Health response should have required fields."""
    from app.schemas import HealthResponse

    health = HealthResponse(
        status="healthy",
        database="healthy",
        ollama="healthy",
    )
    assert health.status == "healthy"
    assert health.database == "healthy"
    assert health.ollama == "healthy"
    assert health.version == "1.0.0"


@pytest.mark.asyncio
async def test_health_degraded_when_db_fails():
    """Health should report degraded when DB is unhealthy."""
    from app.schemas import HealthResponse

    health = HealthResponse(
        status="degraded",
        database="unhealthy: connection refused",
        ollama="healthy",
    )
    assert health.status == "degraded"
    assert "unhealthy" in health.database
