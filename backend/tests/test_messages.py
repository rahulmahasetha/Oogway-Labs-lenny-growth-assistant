"""Tests for message handling and persistence."""

import pytest
import uuid
from datetime import datetime, timezone

from app.schemas import MessageCreate, MessageResponse, ArtifactData
from app.models import Message


def test_message_create_validation():
    """MessageCreate should enforce min/max length."""
    msg = MessageCreate(content="Hello, how does Duolingo grow?")
    assert msg.content == "Hello, how does Duolingo grow?"


def test_message_create_empty_rejected():
    """MessageCreate should reject empty content."""
    with pytest.raises(Exception):
        MessageCreate(content="")


def test_message_create_too_long_rejected():
    """MessageCreate should reject content over 10000 chars."""
    with pytest.raises(Exception):
        MessageCreate(content="x" * 10001)


def test_message_response_schema():
    """MessageResponse should serialize correctly."""
    response = MessageResponse(
        id=uuid.uuid4(),
        session_id=uuid.uuid4(),
        role="assistant",
        content="Based on the transcripts...",
        sources=[],
        artifact=None,
        created_at=datetime.now(timezone.utc),
    )
    assert response.role == "assistant"
    assert response.artifact is None


def test_message_response_with_artifact():
    """MessageResponse should include artifact when present."""
    artifact = ArtifactData(
        type="markdown",
        content="# Essay\n\nContent here",
        title="Test Essay",
    )
    response = MessageResponse(
        id=uuid.uuid4(),
        session_id=uuid.uuid4(),
        role="assistant",
        content="Here's your essay",
        artifact=artifact,
        created_at=datetime.now(timezone.utc),
    )
    assert response.artifact is not None
    assert response.artifact.type == "markdown"


def test_message_model_roles():
    """Message should accept user and assistant roles."""
    user_msg = Message(role="user", content="Question?", session_id=uuid.uuid4())
    assert user_msg.role == "user"

    asst_msg = Message(role="assistant", content="Answer.", session_id=uuid.uuid4())
    assert asst_msg.role == "assistant"


def test_message_persistence_fields():
    """Message should store sources and artifact as JSONB."""
    msg = Message(
        id=uuid.uuid4(),
        session_id=uuid.uuid4(),
        role="assistant",
        content="Test",
        sources=[{"id": "abc", "title": "Episode 1"}],
        artifact={"type": "markdown", "content": "# Hello"},
    )
    assert isinstance(msg.sources, list)
    assert isinstance(msg.artifact, dict)
