"""Message handling endpoints — the core chat flow."""

from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models import Message, Session
from app.schemas import MessageCreate, MessageResponse
from app.services.agent import generate_response
from app.utils.errors import NotFoundError
from app.utils.logging import get_logger

logger = get_logger("messages")
router = APIRouter()


@router.post(
    "/sessions/{session_id}/messages",
    response_model=MessageResponse,
)
async def send_message(
    session_id: UUID,
    body: MessageCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Send a user message and get an AI response.

    Flow:
    1. Validate session exists
    2. Persist user message
    3. Load session history
    4. Retrieve relevant transcript chunks (RAG)
    5. Generate grounded AI response
    6. Persist assistant message with sources and artifact
    7. Return assistant message
    """
    # 1. Validate session
    result = await db.execute(
        select(Session)
        .where(Session.id == session_id)
        .options(selectinload(Session.messages))
    )
    session = result.scalar_one_or_none()
    if not session:
        raise NotFoundError("Session", str(session_id))

    # 2. Persist user message
    user_msg = Message(
        session_id=session_id,
        role="user",
        content=body.content,
    )
    db.add(user_msg)
    await db.flush()

    # 3. Generate AI response (includes RAG retrieval)
    logger.info("generating_response", session_id=str(session_id), query_len=len(body.content))
    response = await generate_response(
        query=body.content,
        session_messages=session.messages,
        db=db,
    )

    # 4. Persist assistant message
    assistant_msg = Message(
        session_id=session_id,
        role="assistant",
        content=response["content"],
        sources=response.get("sources"),
        artifact=response.get("artifact"),
    )
    db.add(assistant_msg)
    await db.flush()

    # 5. Update session title from first message
    if len(session.messages) <= 2:  # user + assistant = first exchange
        title = body.content[:80] + ("..." if len(body.content) > 80 else "")
        session.title = title

    logger.info(
        "response_generated",
        session_id=str(session_id),
        response_len=len(response["content"]),
        sources_count=len(response.get("sources") or []),
        has_artifact=response.get("artifact") is not None,
    )

    return assistant_msg
