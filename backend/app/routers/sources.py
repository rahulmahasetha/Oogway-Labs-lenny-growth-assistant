"""Source detail endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Source
from app.schemas import SourceDetail
from app.utils.errors import NotFoundError

router = APIRouter()


@router.get("/sources/{source_id}", response_model=SourceDetail)
async def get_source(source_id: UUID, db: AsyncSession = Depends(get_db)):
    """Get full details for a source (podcast episode or newsletter)."""
    result = await db.execute(select(Source).where(Source.id == source_id))
    source = result.scalar_one_or_none()
    if not source:
        raise NotFoundError("Source", str(source_id))
    return source
