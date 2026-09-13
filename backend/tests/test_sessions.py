"""Tests for session management."""

import pytest
import uuid
from unittest.mock import AsyncMock, MagicMock, patch

from app.schemas import SessionCreate, SessionSummary, SessionDetail
from app.models import Session


def test_session_create_defaults():
    """SessionCreate should default to 'New Chat'."""
    sc = SessionCreate()
    assert sc.title == "New Chat"


def test_session_create_custom_title():
    """SessionCreate should accept custom titles."""
    sc = SessionCreate(title="My Chat")
    assert sc.title == "My Chat"


def test_session_summary_schema():
    """SessionSummary should serialize correctly."""
    from datetime import datetime, timezone
    
    summary = SessionSummary(
        id=uuid.uuid4(),
        title="Test Chat",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    assert summary.title == "Test Chat"


def test_session_detail_with_empty_messages():
    """SessionDetail should work with empty messages list."""
    from datetime import datetime, timezone
    
    detail = SessionDetail(
        id=uuid.uuid4(),
        title="Test",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        messages=[],
    )
    assert detail.messages == []


def test_session_model():
    """Session ORM model should have correct defaults."""
    session = Session(title="Test")
    assert session.title == "Test"
    # id is generated on insert
    assert session.id is None


def test_session_isolation():
    """Different sessions should have different IDs."""
    s1 = Session(id=uuid.uuid4(), title="Chat 1")
    s2 = Session(id=uuid.uuid4(), title="Chat 2")
    assert s1.id != s2.id
