"""Tests for the ingestion pipeline."""

import pytest
from app.services.ingestion import (
    chunk_podcast_transcript,
    chunk_newsletter,
    parse_frontmatter,
)
from app.services.ship30 import is_essay_request
from app.services.artifacts import is_artifact_request, is_html_request


class TestChunkingPodcast:
    """Tests for podcast transcript chunking."""

    def test_basic_chunking(self):
        """Should split by speaker turns."""
        content = """**Speaker A** (00:00:00):
This is the first part of the conversation about product management.

**Speaker B** (00:01:00):
And here is the response about growth strategies.

**Speaker A** (00:02:00):
Let me follow up on that point.
"""
        chunks = chunk_podcast_transcript(content, max_chunk_size=500)
        assert len(chunks) >= 1
        assert chunks[0]["speaker"] == "Speaker A"
        assert chunks[0]["start_time"] == "00:00:00"

    def test_preserves_content(self):
        """Chunks should contain the actual content."""
        content = """**Guest** (00:00:00):
Important insight about growth.
"""
        chunks = chunk_podcast_transcript(content)
        assert any("growth" in c["content"] for c in chunks)

    def test_chunk_index_sequential(self):
        """Chunk indices should be sequential."""
        content = """**A** (00:00:00):
First point. """ + "x " * 500 + """

**B** (00:05:00):
Second point. """ + "y " * 500 + """

**A** (00:10:00):
Third point. """ + "z " * 500
        chunks = chunk_podcast_transcript(content, max_chunk_size=200)
        indices = [c["chunk_index"] for c in chunks]
        assert indices == list(range(len(indices)))


class TestChunkingNewsletter:
    """Tests for newsletter chunking."""

    def test_basic_newsletter_chunking(self):
        """Should split newsletter by sections."""
        content = """### Section One

Some content here about product management best practices.

### Section Two

More content about growth strategies and metrics.
"""
        chunks = chunk_newsletter(content)
        assert len(chunks) >= 1

    def test_newsletter_no_speaker(self):
        """Newsletter chunks should not have speaker."""
        content = "Some newsletter content about growth."
        chunks = chunk_newsletter(content)
        for chunk in chunks:
            assert chunk["speaker"] is None


class TestSkillDetection:
    """Tests for skill routing detection."""

    def test_essay_detection_positive(self):
        """Should detect essay requests."""
        assert is_essay_request("Write an essay about growth")
        assert is_essay_request("Generate a Ship 30 post")
        assert is_essay_request("Write me a long-form article about AI")
        assert is_essay_request("Can you write a deep dive on retention?")

    def test_essay_detection_negative(self):
        """Should not detect regular questions as essays."""
        assert not is_essay_request("What is growth?")
        assert not is_essay_request("How does Duolingo retain users?")
        assert not is_essay_request("Tell me about AI")

    def test_artifact_detection_positive(self):
        """Should detect artifact requests."""
        assert is_artifact_request("Create a document about growth strategies")
        assert is_artifact_request("Generate a report on AI trends")
        assert is_artifact_request("Make a cheatsheet for product managers")

    def test_artifact_detection_negative(self):
        """Should not detect regular questions as artifact requests."""
        assert not is_artifact_request("What is a document?")
        assert not is_artifact_request("How do you create growth?")

    def test_html_detection(self):
        """Should detect HTML-specific requests."""
        assert is_html_request("Create a styled HTML document")
        assert is_html_request("Generate a formatted report")
        assert not is_html_request("Write a plain text summary")


class TestFrontmatter:
    """Tests for frontmatter parsing."""

    def test_parse_podcast_frontmatter(self):
        """Should parse podcast metadata correctly."""
        import tempfile
        import os

        content = """---
title: "Test Episode"
type: "podcast"
guest: "Test Guest"
date: "2026-01-01"
---

**Test Guest** (00:00:00):
Content here.
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(content)
            f.flush()
            metadata, body = parse_frontmatter(f.name)

        os.unlink(f.name)

        assert metadata["title"] == "Test Episode"
        assert metadata["type"] == "podcast"
        assert metadata["guest"] == "Test Guest"
        assert "Content here" in body
