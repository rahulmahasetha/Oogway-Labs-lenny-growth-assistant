"""SQLAlchemy ORM models for the Lenny Growth Assistant."""

import uuid
from datetime import datetime, timezone

from pgvector.sqlalchemy import Vector
from sqlalchemy import Column, DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from app.database import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


class Source(Base):
    """A podcast episode or newsletter article."""

    __tablename__ = "sources"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(Text, nullable=False)
    source_type = Column(String(20), nullable=False)  # 'podcast' or 'newsletter'
    guest = Column(String(255), nullable=True)
    date = Column(DateTime, nullable=True)
    post_url = Column(Text, nullable=True)
    youtube_url = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    word_count = Column(Integer, nullable=True)
    file_path = Column(Text, nullable=False, unique=True)  # prevents duplicate ingestion
    created_at = Column(DateTime, default=utcnow, nullable=False)

    # Relationships
    chunks = relationship("Chunk", back_populates="source", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Source {self.title!r}>"


class Chunk(Base):
    """A text chunk from a source with its embedding vector."""

    __tablename__ = "chunks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_id = Column(
        UUID(as_uuid=True), ForeignKey("sources.id", ondelete="CASCADE"), nullable=False
    )
    content = Column(Text, nullable=False)
    chunk_index = Column(Integer, nullable=False)
    speaker = Column(String(255), nullable=True)  # for podcast transcripts
    start_time = Column(String(20), nullable=True)  # for podcast transcripts
    embedding = Column(Vector(384), nullable=False)  # all-MiniLM-L6-v2 = 384 dims
    created_at = Column(DateTime, default=utcnow, nullable=False)

    # Relationships
    source = relationship("Source", back_populates="chunks")

    __table_args__ = (
        Index("idx_chunks_source", "source_id"),
    )

    def __repr__(self):
        return f"<Chunk {self.id} from {self.source_id}>"


class Session(Base):
    """An independent chat session."""

    __tablename__ = "sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), default="New Chat", nullable=False)
    user_metadata = Column(JSONB, nullable=True)  # user metadata as requested in assignment
    created_at = Column(DateTime, default=utcnow, nullable=False)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow, nullable=False)

    # Relationships
    messages = relationship(
        "Message", back_populates="session", cascade="all, delete-orphan",
        order_by="Message.created_at"
    )

    def __repr__(self):
        return f"<Session {self.id} {self.title!r}>"


class Message(Base):
    """A single message within a chat session."""

    __tablename__ = "messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(
        UUID(as_uuid=True), ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False
    )
    role = Column(String(20), nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    sources = Column(JSONB, nullable=True)  # cited source references
    artifact = Column(JSONB, nullable=True)  # {type: 'markdown'|'html', content: '...'}
    created_at = Column(DateTime, default=utcnow, nullable=False)

    # Relationships
    session = relationship("Session", back_populates="messages")

    __table_args__ = (
        Index("idx_messages_session_created", "session_id", "created_at"),
    )

    def __repr__(self):
        return f"<Message {self.role} in {self.session_id}>"
