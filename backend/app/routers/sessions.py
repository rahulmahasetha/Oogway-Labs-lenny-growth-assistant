"""Session management endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models import Session
from app.schemas import SessionCreate, SessionDetail, SessionSummary, SessionUpdate
from app.utils.errors import NotFoundError
from app.utils.logging import get_logger

logger = get_logger("sessions")
router = APIRouter()


@router.post("/sessions", response_model=SessionSummary, status_code=201)
async def create_session(
    body: SessionCreate = SessionCreate(),
    db: AsyncSession = Depends(get_db),
):
    """Create a new chat session."""
    session = Session(title=body.title or "New Chat")
    db.add(session)
    await db.flush()
    logger.info("session_created", session_id=str(session.id))
    return session


@router.get("/sessions", response_model=list[SessionSummary])
async def list_sessions(db: AsyncSession = Depends(get_db)):
    """List all chat sessions, newest first."""
    result = await db.execute(
        select(Session).order_by(Session.updated_at.desc())
    )
    return result.scalars().all()


@router.get("/sessions/{session_id}", response_model=SessionDetail)
async def get_session(session_id: UUID, db: AsyncSession = Depends(get_db)):
    """Get a session with its full message history."""
    result = await db.execute(
        select(Session)
        .where(Session.id == session_id)
        .options(selectinload(Session.messages))
    )
    session = result.scalar_one_or_none()
    if not session:
        raise NotFoundError("Session", str(session_id))
    return session


@router.patch("/sessions/{session_id}", response_model=SessionSummary)
async def update_session(
    session_id: UUID,
    session_in: SessionUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update a session's title."""
    result = await db.execute(select(Session).where(Session.id == session_id))
    session = result.scalar_one_or_none()
    if not session:
        raise NotFoundError("Session", str(session_id))
    if session_in.title is not None:
        session.title = session_in.title
    await db.flush()
    logger.info("session_updated", session_id=str(session_id))
    return session


@router.delete("/sessions/{session_id}", status_code=204)
async def delete_session(session_id: UUID, db: AsyncSession = Depends(get_db)):
    """Delete a session and all its messages."""
    result = await db.execute(select(Session).where(Session.id == session_id))
    session = result.scalar_one_or_none()
    if not session:
        raise NotFoundError("Session", str(session_id))
    await db.delete(session)
    logger.info("session_deleted", session_id=str(session_id))
