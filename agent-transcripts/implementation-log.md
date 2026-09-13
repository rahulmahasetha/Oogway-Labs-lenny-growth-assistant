# Agent Transcripts

This directory records important coding-agent interactions during the implementation of the Lenny Growth Assistant.

## Implementation Decisions

### 1. Python 3.12 Requirement
**Issue**: The system had Python 3.14 as default, but `pydantic-core` doesn't yet support Python 3.14 (PyO3 version 0.24.0 maxes out at 3.13).
**Decision**: Use Python 3.12 for the backend virtual environment. Dockerfile already uses `python:3.12-slim`.
**Impact**: None — Python 3.12 is the standard production Python version.

### 2. Embedding Model Choice
**Decision**: `sentence-transformers/all-MiniLM-L6-v2` (384 dimensions)
**Rationale**: 
- Free, no API key required
- Fast inference (~50ms per query)
- Small footprint (~80MB)
- Good quality for English text retrieval
- Pre-downloaded at Docker build time for faster startup
**Trade-off**: Lower dimensionality than OpenAI's `text-embedding-3-small` (1536-dim), but avoids API key dependency.

### 3. pgvector Over Dedicated Vector DB
**Decision**: Use PostgreSQL with pgvector instead of a separate vector database (Pinecone, Qdrant, etc.)
**Rationale**:
- Single database service simplifies deployment
- Avoids introducing another service to Docker Compose
- Sufficient for 60 documents (~3000 chunks)
- pgvector cosine similarity search is fast enough for this scale
**Trade-off**: Would need to reconsider at 100K+ documents scale.

### 4. Chunking Strategy
**Decision**: ~2000 character chunks with 200 character overlap
**Rationale**:
- Podcast chunks preserve speaker turn boundaries
- Newsletter chunks preserve section/heading boundaries
- Overlap ensures context isn't lost at chunk boundaries
- 2000 chars ≈ 400-500 tokens, fits well within LLM context
**Failed alternative considered**: Fixed-size chunking at 500 chars — too short, lost context between speaker turns.

### 5. Artifact Security — Sandboxed Iframe
**Decision**: Use `sandbox=""` (maximum restriction) for HTML artifacts
**Rationale**:
- No `allow-same-origin` prevents access to parent window
- No `allow-scripts` prevents JavaScript execution entirely
- `srcdoc` attribute avoids network requests
- LLM prompt explicitly forbids JavaScript in generated HTML
**Trade-off**: CSS animations in generated HTML won't work since scripts are blocked. Acceptable since security > aesthetics for untrusted content.

### 6. Provider Factory Pattern
**Decision**: Singleton factory with abstract base class
**Rationale**:
- Clean abstraction — adding a new provider requires one class and one factory case
- Singleton avoids re-creating expensive client connections
- `reset_provider()` method enables testing
**Alternative considered**: Dependency injection via FastAPI — more complex, not needed for 3 providers.

## Bugs Discovered & Fixed

### 1. YAML Frontmatter Inconsistency
**Bug**: Some podcast files have `post_url` while others have `youtube_url`. Some have `channel`, some don't.
**Fix**: Made all metadata fields optional in the Source model. Parse what's available, skip what's missing.

### 2. Empty Speaker Turns
**Bug**: Some podcast transcripts have back-to-back speaker headers with no content between them.
**Fix**: Added filtering to remove empty turns: `turns = [t for t in turns if t["text"]]`

## Testing Results

Tests cover:
- Schema validation (create, serialize, reject invalid)
- Session isolation (different UUIDs)
- RAG context building and citation de-duplication
- Provider factory (Ollama, missing API keys, unknown provider, singleton)
- Ingestion chunking (podcast turns, newsletter sections, indices)
- Skill detection (essay, artifact, HTML keywords)
- Frontmatter parsing
