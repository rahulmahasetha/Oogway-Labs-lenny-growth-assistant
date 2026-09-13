"""Pytest configuration and shared fixtures."""

import os
import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

# Set test environment variables before any imports
os.environ["DATABASE_URL"] = "postgresql+asyncpg://lenny:lenny_secret@localhost:5432/lenny_growth_test"
os.environ["LLM_PROVIDER"] = "ollama"
os.environ["OLLAMA_BASE_URL"] = "http://localhost:11434"
os.environ["DATA_DIR"] = "./data"
os.environ["LOG_LEVEL"] = "WARNING"


@pytest.fixture
def mock_db():
    """Create a mock async database session."""
    db = AsyncMock()
    db.execute = AsyncMock()
    db.flush = AsyncMock()
    db.commit = AsyncMock()
    db.rollback = AsyncMock()
    db.close = AsyncMock()
    db.add = MagicMock()
    db.delete = AsyncMock()
    db.scalar = AsyncMock(return_value=0)
    return db


@pytest.fixture
def sample_session_id():
    return uuid.uuid4()


@pytest.fixture
def sample_source_id():
    return uuid.uuid4()


@pytest.fixture
def sample_chunks():
    """Sample RAG retrieval results."""
    return [
        {
            "chunk_id": str(uuid.uuid4()),
            "chunk_content": "Adam Mosseri explains that small teams are more effective because there are fewer people to coordinate.",
            "speaker": "Adam Mosseri",
            "start_time": "00:03:57",
            "source_id": str(uuid.uuid4()),
            "title": "Adam Mosseri: AI is a tailwind for authenticity",
            "source_type": "podcast",
            "guest": "Adam Mosseri",
            "post_url": "https://www.lennysnewsletter.com/p/adam-mosseri-ai-is-a-tailwind-for",
            "similarity": 0.82,
        },
        {
            "chunk_id": str(uuid.uuid4()),
            "chunk_content": "Simon Willison describes how coding agents can generate thousands of lines of code per day.",
            "speaker": "Simon Willison",
            "start_time": "00:00:00",
            "source_id": str(uuid.uuid4()),
            "title": "An AI state of the union | Simon Willison",
            "source_type": "podcast",
            "guest": "Simon Willison",
            "post_url": None,
            "similarity": 0.75,
        },
    ]
