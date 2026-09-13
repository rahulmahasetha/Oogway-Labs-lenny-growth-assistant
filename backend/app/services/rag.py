"""
RAG retrieval service.

Strategy:
- Embeds the user query with the same model used for ingestion
- Performs cosine similarity search via pgvector
- Returns top-k chunks above the similarity threshold
- De-duplicates by source to provide breadth
- Builds a grounded context string with source attribution
"""

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.services.ingestion import get_embedding_model
from app.utils.logging import get_logger

logger = get_logger("rag")


async def retrieve_relevant_chunks(
    query: str,
    db: AsyncSession,
    top_k: int | None = None,
    threshold: float | None = None,
) -> list[dict]:
    """
    Retrieve transcript chunks relevant to the query.

    Returns a list of dicts with keys:
    - source_id, title, source_type, guest, post_url
    - chunk_content, speaker, start_time
    - similarity (cosine)
    """
    top_k = top_k or settings.rag_top_k
    threshold = threshold or settings.rag_similarity_threshold

    # Embed the query
    model = get_embedding_model()
    query_embedding = model.encode(query).tolist()

    # pgvector cosine similarity search
    # 1 - cosine_distance = cosine_similarity
    sql = text("""
        SELECT
            c.id AS chunk_id,
            c.content AS chunk_content,
            c.speaker,
            c.start_time,
            c.chunk_index,
            s.id AS source_id,
            s.title,
            s.source_type,
            s.guest,
            s.post_url,
            1 - (c.embedding <=> CAST(:embedding AS vector)) AS similarity
        FROM chunks c
        JOIN sources s ON c.source_id = s.id
        WHERE 1 - (c.embedding <=> CAST(:embedding AS vector)) > :threshold
        ORDER BY c.embedding <=> CAST(:embedding AS vector)
        LIMIT :top_k
    """)

    result = await db.execute(
        sql,
        {
            "embedding": str(query_embedding),
            "threshold": threshold,
            "top_k": top_k,
        },
    )
    rows = result.fetchall()

    chunks = []
    for row in rows:
        chunks.append({
            "chunk_id": str(row.chunk_id),
            "chunk_content": row.chunk_content,
            "speaker": row.speaker,
            "start_time": row.start_time,
            "source_id": str(row.source_id),
            "title": row.title,
            "source_type": row.source_type,
            "guest": row.guest,
            "post_url": row.post_url,
            "similarity": float(row.similarity),
        })

    logger.info(
        "rag_retrieval",
        query_preview=query[:80],
        results=len(chunks),
        top_similarity=chunks[0]["similarity"] if chunks else 0,
    )

    return chunks


def build_context(chunks: list[dict]) -> str:
    """
    Build a context string from retrieved chunks for the LLM prompt.

    Each chunk is attributed with its source title, guest, and timestamp.
    """
    if not chunks:
        return ""

    context_parts = []
    for i, chunk in enumerate(chunks, 1):
        header = f"[Source {i}: \"{chunk['title']}\""
        if chunk.get("guest"):
            header += f" — {chunk['guest']}"
        if chunk.get("start_time"):
            header += f" at {chunk['start_time']}"
        header += "]"

        context_parts.append(f"{header}\n{chunk['chunk_content']}")

    return "\n\n---\n\n".join(context_parts)


def build_source_citations(chunks: list[dict]) -> list[dict]:
    """
    De-duplicate chunks by source and return citation summaries.
    """
    seen_sources = set()
    citations = []

    for chunk in chunks:
        source_id = chunk["source_id"]
        if source_id not in seen_sources:
            seen_sources.add(source_id)
            citations.append({
                "id": source_id,
                "title": chunk["title"],
                "source_type": chunk["source_type"],
                "guest": chunk.get("guest"),
                "post_url": chunk.get("post_url"),
                "chunk_content": chunk["chunk_content"][:200] + "...",
                "speaker": chunk.get("speaker"),
                "start_time": chunk.get("start_time"),
                "similarity": chunk["similarity"],
            })

    return citations
