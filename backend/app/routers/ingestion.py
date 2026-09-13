"""Ingestion endpoints for loading transcripts."""

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Chunk, Source
from app.schemas import IngestionResult, IngestionStatus
from app.services.ingestion import run_ingestion
from app.utils.logging import get_logger

logger = get_logger("ingestion")
router = APIRouter()


@router.post("/ingestion/run", response_model=IngestionResult)
async def trigger_ingestion(db: AsyncSession = Depends(get_db)):
    """Run the transcript ingestion pipeline."""
    logger.info("ingestion_triggered")
    result = await run_ingestion(db)
    logger.info(
        "ingestion_complete",
        sources=result.sources_processed,
        chunks=result.chunks_created,
        skipped=result.sources_skipped,
        errors=len(result.errors),
    )
    return result


@router.get("/ingestion/status", response_model=IngestionStatus)
async def ingestion_status(db: AsyncSession = Depends(get_db)):
    """Get current ingestion statistics."""
    total_sources = await db.scalar(select(func.count(Source.id)))
    total_chunks = await db.scalar(select(func.count(Chunk.id)))
    podcasts = await db.scalar(
        select(func.count(Source.id)).where(Source.source_type == "podcast")
    )
    newsletters = await db.scalar(
        select(func.count(Source.id)).where(Source.source_type == "newsletter")
    )

    return IngestionStatus(
        total_sources=total_sources or 0,
        total_chunks=total_chunks or 0,
        podcasts=podcasts or 0,
        newsletters=newsletters or 0,
    )
