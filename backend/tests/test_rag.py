"""Tests for RAG retrieval service."""

import pytest
from app.services.rag import build_context, build_source_citations


def test_build_context_empty():
    """build_context should return empty string for no chunks."""
    assert build_context([]) == ""


def test_build_context_formats_correctly(sample_chunks):
    """build_context should format chunks with source attribution."""
    context = build_context(sample_chunks)
    assert "Adam Mosseri" in context
    assert "Simon Willison" in context
    assert "Source 1" in context
    assert "Source 2" in context
    assert "---" in context  # separator


def test_build_context_includes_timestamps(sample_chunks):
    """build_context should include timestamps when available."""
    context = build_context(sample_chunks)
    assert "00:03:57" in context


def test_build_source_citations_deduplicates(sample_chunks):
    """build_source_citations should de-duplicate by source_id."""
    citations = build_source_citations(sample_chunks)
    assert len(citations) == 2  # two unique sources


def test_build_source_citations_duplicate_source():
    """build_source_citations should only include each source once."""
    source_id = "abc-123"
    chunks = [
        {"source_id": source_id, "title": "Episode 1", "source_type": "podcast",
         "guest": "Guest 1", "post_url": "https://example.com",
         "chunk_content": "Content 1", "speaker": "Guest", "start_time": "00:00",
         "similarity": 0.8},
        {"source_id": source_id, "title": "Episode 1", "source_type": "podcast",
         "guest": "Guest 1", "post_url": "https://example.com",
         "chunk_content": "Content 2", "speaker": "Guest", "start_time": "00:05",
         "similarity": 0.7},
    ]
    citations = build_source_citations(chunks)
    assert len(citations) == 1


def test_build_source_citations_preserves_metadata(sample_chunks):
    """Citations should include title, type, guest, and URL."""
    citations = build_source_citations(sample_chunks)
    first = citations[0]
    assert "title" in first
    assert "source_type" in first
    assert "guest" in first
    assert "post_url" in first
    assert "similarity" in first


def test_empty_retrieval_returns_empty():
    """Empty retrieval should produce empty citations."""
    citations = build_source_citations([])
    assert citations == []
