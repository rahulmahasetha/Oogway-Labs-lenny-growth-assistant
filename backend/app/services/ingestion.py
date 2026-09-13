"""
Transcript ingestion pipeline.

Strategy:
- Loads all .md files from data/podcasts/ and data/newsletters/
- Parses YAML frontmatter for metadata (title, guest, date, URLs, etc.)
- Chunks content preserving speaker turns for podcasts
- Generates embeddings with sentence-transformers (all-MiniLM-L6-v2)
- Stores in PostgreSQL with pgvector
- Idempotent: skips files already ingested (via unique file_path constraint)
"""

import re
import uuid
from pathlib import Path

import frontmatter
from sentence_transformers import SentenceTransformer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models import Chunk, Source
from app.schemas import IngestionResult
from app.utils.logging import get_logger

logger = get_logger("ingestion")

# Lazy-loaded embedding model singleton
_embedding_model: SentenceTransformer | None = None


def get_embedding_model() -> SentenceTransformer:
    """Get or create the embedding model singleton."""
    global _embedding_model
    if _embedding_model is None:
        logger.info("loading_embedding_model", model=settings.embedding_model)
        _embedding_model = SentenceTransformer(settings.embedding_model)
    return _embedding_model


def parse_frontmatter(file_path: str) -> tuple[dict, str]:
    """Parse YAML frontmatter and body from a markdown file."""
    with open(file_path, "r", encoding="utf-8") as f:
        post = frontmatter.load(f)
    return dict(post.metadata), post.content


def chunk_podcast_transcript(content: str, max_chunk_size: int = 2000, overlap: int = 200) -> list[dict]:
    """
    Chunk a podcast transcript preserving speaker turns.

    Each chunk retains the speaker name and timestamp from the first turn.
    If a single speaker turn exceeds max_chunk_size, it is split with overlap.
    """
    # Match speaker turns: **Speaker Name** (HH:MM:SS):
    turn_pattern = re.compile(
        r'\*\*([^*]+)\*\*\s*\((\d{2}:\d{2}:\d{2})\):\s*\n?'
    )

    turns = []
    last_end = 0
    for match in turn_pattern.finditer(content):
        if last_end > 0:
            turn_text = content[last_end:match.start()].strip()
            if turn_text:
                turns[-1]["text"] = turn_text
        turns.append({
            "speaker": match.group(1).strip(),
            "timestamp": match.group(2),
            "text": "",
            "start": match.end(),
        })
        last_end = match.end()

    # Capture last turn's text
    if turns:
        turns[-1]["text"] = content[last_end:].strip()

    # Remove empty turns
    turns = [t for t in turns if t["text"]]

    # Group turns into chunks
    chunks = []
    current_chunk = ""
    current_speaker = ""
    current_timestamp = ""
    chunk_index = 0

    for turn in turns:
        turn_text = f"**{turn['speaker']}** ({turn['timestamp']}):\n{turn['text']}\n\n"

        if len(current_chunk) + len(turn_text) > max_chunk_size and current_chunk:
            chunks.append({
                "content": current_chunk.strip(),
                "speaker": current_speaker,
                "start_time": current_timestamp,
                "chunk_index": chunk_index,
            })
            chunk_index += 1
            # Overlap: keep the last portion
            if len(current_chunk) > overlap:
                current_chunk = current_chunk[-overlap:]
            else:
                current_chunk = ""

        if not current_chunk:
            current_speaker = turn["speaker"]
            current_timestamp = turn["timestamp"]

        current_chunk += turn_text

    # Add final chunk
    if current_chunk.strip():
        chunks.append({
            "content": current_chunk.strip(),
            "speaker": current_speaker,
            "start_time": current_timestamp,
            "chunk_index": chunk_index,
        })

    return chunks


def chunk_newsletter(content: str, max_chunk_size: int = 2000, overlap: int = 200) -> list[dict]:
    """
    Chunk a newsletter article by sections/paragraphs.

    Splits on headings (###) first, then on double newlines if chunks are too large.
    """
    # Split on headings
    sections = re.split(r'\n(?=#{1,4}\s)', content)

    chunks = []
    chunk_index = 0

    for section in sections:
        section = section.strip()
        if not section:
            continue

        if len(section) <= max_chunk_size:
            chunks.append({
                "content": section,
                "speaker": None,
                "start_time": None,
                "chunk_index": chunk_index,
            })
            chunk_index += 1
        else:
            # Split long sections by paragraphs
            paragraphs = section.split("\n\n")
            current = ""
            for para in paragraphs:
                if len(current) + len(para) + 2 > max_chunk_size and current:
                    chunks.append({
                        "content": current.strip(),
                        "speaker": None,
                        "start_time": None,
                        "chunk_index": chunk_index,
                    })
                    chunk_index += 1
                    if len(current) > overlap:
                        current = current[-overlap:]
                    else:
                        current = ""
                current += para + "\n\n"

            if current.strip():
                chunks.append({
                    "content": current.strip(),
                    "speaker": None,
                    "start_time": None,
                    "chunk_index": chunk_index,
                })
                chunk_index += 1

    return chunks


async def run_ingestion(db: AsyncSession) -> IngestionResult:
    """
    Run the full ingestion pipeline.

    1. Scan data directories for .md files
    2. Parse frontmatter and content
    3. Chunk content
    4. Generate embeddings
    5. Store in database

    Idempotent: files already in the database (by file_path) are skipped.
    """
    data_dir = Path(settings.data_dir)
    model = get_embedding_model()

    result = IngestionResult(
        sources_processed=0,
        chunks_created=0,
        sources_skipped=0,
    )

    # Collect all markdown files
    md_files = []
    for subdir in ["podcasts", "newsletters"]:
        dir_path = data_dir / subdir
        if dir_path.exists():
            for f in sorted(dir_path.glob("*.md")):
                md_files.append(f)

    logger.info("ingestion_scanning", files_found=len(md_files))

    for file_path in md_files:
        rel_path = str(file_path.relative_to(data_dir))

        # Check if already ingested
        existing = await db.execute(
            select(Source).where(Source.file_path == rel_path)
        )
        if existing.scalar_one_or_none():
            result.sources_skipped += 1
            continue

        try:
            # Parse frontmatter
            metadata, content = parse_frontmatter(str(file_path))

            if not content.strip():
                result.errors.append(f"{rel_path}: empty content")
                continue

            source_type = metadata.get("type", "podcast")

            date_val = metadata.get("date")
            if isinstance(date_val, str):
                try:
                    from datetime import datetime, timezone
                    date_val = datetime.strptime(date_val, "%Y-%m-%d").replace(tzinfo=timezone.utc)
                except ValueError:
                    date_val = None

            # Create source record
            source = Source(
                id=uuid.uuid4(),
                title=metadata.get("title", file_path.stem),
                source_type=source_type,
                guest=metadata.get("guest"),
                date=date_val,
                post_url=metadata.get("post_url"),
                youtube_url=metadata.get("youtube_url"),
                description=metadata.get("description"),
                word_count=metadata.get("word_count"),
                file_path=rel_path,
            )
            db.add(source)

            # Chunk content
            if source_type == "podcast":
                raw_chunks = chunk_podcast_transcript(content)
            else:
                raw_chunks = chunk_newsletter(content)

            if not raw_chunks:
                result.errors.append(f"{rel_path}: no chunks generated")
                continue

            # Generate embeddings in batch
            texts = [c["content"] for c in raw_chunks]
            embeddings = model.encode(texts, show_progress_bar=False)

            # Create chunk records
            for chunk_data, embedding in zip(raw_chunks, embeddings):
                chunk = Chunk(
                    id=uuid.uuid4(),
                    source_id=source.id,
                    content=chunk_data["content"],
                    chunk_index=chunk_data["chunk_index"],
                    speaker=chunk_data.get("speaker"),
                    start_time=chunk_data.get("start_time"),
                    embedding=embedding.tolist(),
                )
                db.add(chunk)

            result.sources_processed += 1
            result.chunks_created += len(raw_chunks)
            logger.info(
                "source_ingested",
                file=rel_path,
                chunks=len(raw_chunks),
                source_type=source_type,
            )

        except Exception as e:
            result.errors.append(f"{rel_path}: {e!s}")
            logger.error("ingestion_error", file=rel_path, error=str(e))

    return result
