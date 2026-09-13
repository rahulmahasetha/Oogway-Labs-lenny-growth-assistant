"""Pydantic schemas for API request/response validation."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

# --- Source Schemas ---

class SourceSummary(BaseModel):
    """Brief source info for citations."""
    id: UUID
    title: str
    source_type: str
    guest: str | None = None
    post_url: str | None = None
    chunk_content: str | None = None
    speaker: str | None = None
    start_time: str | None = None
    similarity: float | None = None

    model_config = {"from_attributes": True}


class SourceDetail(BaseModel):
    """Full source details."""
    id: UUID
    title: str
    source_type: str
    guest: str | None = None
    date: datetime | None = None
    post_url: str | None = None
    youtube_url: str | None = None
    description: str | None = None
    word_count: int | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


# --- Artifact Schema ---

class ArtifactData(BaseModel):
    """An artifact (rendered document) attached to a message."""
    type: str = Field(description="'markdown' or 'html'")
    content: str = Field(description="The artifact content")
    title: str | None = None


# --- Message Schemas ---

class MessageCreate(BaseModel):
    """Request body for sending a message."""
    content: str = Field(..., min_length=1, max_length=10000)


class MessageResponse(BaseModel):
    """A single message in the conversation."""
    id: UUID
    session_id: UUID
    role: str
    content: str
    sources: list[SourceSummary] | None = None
    artifact: ArtifactData | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


# --- Session Schemas ---

class SessionCreate(BaseModel):
    """Request body for creating a session."""
    title: str | None = "New Chat"


class SessionUpdate(BaseModel):
    """Request body for updating a session."""
    title: str | None = None


class SessionSummary(BaseModel):
    """Brief session info for the sidebar list."""
    id: UUID
    title: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class SessionDetail(BaseModel):
    """Full session with messages."""
    id: UUID
    title: str
    created_at: datetime
    updated_at: datetime
    messages: list[MessageResponse] = []

    model_config = {"from_attributes": True}


# --- Ingestion Schemas ---

class IngestionResult(BaseModel):
    """Result of an ingestion run."""
    sources_processed: int
    chunks_created: int
    sources_skipped: int
    errors: list[str] = []


class IngestionStatus(BaseModel):
    """Current state of ingested data."""
    total_sources: int
    total_chunks: int
    podcasts: int
    newsletters: int


# --- Config Schema ---

class AppConfig(BaseModel):
    """Active application configuration exposed to the frontend."""
    llm_provider: str
    llm_model: str
    embedding_model: str
    rag_top_k: int
    rag_similarity_threshold: float


# --- Health Schema ---

class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    database: str
    ollama: str
    version: str = "1.0.0"


# --- Error Schema ---

class ErrorResponse(BaseModel):
    """Structured error response."""
    error: str
    detail: str | None = None
