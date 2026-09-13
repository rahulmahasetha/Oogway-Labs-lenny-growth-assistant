# Product Requirements Document — Lenny Growth Assistant

## 1. Overview

### User
Product managers, growth practitioners, and tech leaders who follow Lenny Rachitsky's content.

### Problem
Lenny's Podcast has 200+ episodes totaling millions of words. Finding specific insights, frameworks, or advice from past episodes requires listening to entire episodes or manually searching transcripts. There is no efficient way to query this knowledge base or generate well-sourced content from it.

### Solution
An AI-powered chat assistant that retrieves and synthesizes knowledge from Lenny's Podcast transcripts and newsletters, providing sourced answers and generating publication-ready essays.

## 2. Success Metric

- **Accuracy**: 95%+ of claims in responses are traceable to transcript content
- **Latency**: < 10s response time for Q&A, < 30s for essays
- **Grounding**: 100% of responses include source citations when drawing from transcripts
- **Usability**: Evaluator can clone, deploy, and query within 10 minutes following README

## 3. Assumptions

- The evaluator has Docker installed
- The dataset (50 podcasts + 10 newsletters) represents a subset; the system is designed for the full corpus
- Ollama is the primary demo model (no API key required)
- Cloud LLM providers require user-supplied API keys

## 4. Scope

### Included
- RAG-powered Q&A grounded in transcripts
- Multi-session chat with PostgreSQL persistence
- Ship 30 for 30 essay generation (~1,250 words)
- Markdown and HTML artifact generation
- In-app artifact viewer with security sandboxing
- Ollama (local) + OpenAI/Anthropic (cloud) support
- Source citations with episode links
- Docker Compose deployment

### Excluded
- User authentication (single-user demo)
- Real-time transcript ingestion from podcast feeds
- Audio playback integration
- Full-text search (only vector similarity)
- Fine-tuned models

## 5. User Flows

### Flow 1: Ask a Question
1. User opens the app → sees welcome screen
2. Clicks "New Chat" → session created
3. Types a question (e.g., "How did Duolingo grow?")
4. System retrieves relevant transcript chunks
5. LLM generates grounded response with citations
6. User sees response + clickable source links

### Flow 2: Generate an Essay
1. User types "Write an essay about product team evolution"
2. System detects essay intent → routes to Ship 30 skill
3. Retrieves relevant chunks → generates ~1,250 word essay
4. Essay appears in the Artifact Viewer
5. Chat shows confirmation + source citations

### Flow 3: Follow-up Conversation
1. User asks initial question → gets response
2. User asks follow-up referencing prior context
3. System loads session history + new RAG results
4. Response maintains conversational continuity

## 6. Acceptance Criteria

- [ ] App starts with `docker compose up`
- [ ] Health endpoint reports DB and Ollama status
- [ ] Ingestion processes all 60 files without errors
- [ ] Chat responds to product management questions with citations
- [ ] Chat sessions are independent (no cross-contamination)
- [ ] Ship 30 essays are ~1,250 words with proper format
- [ ] Artifact Viewer renders Markdown natively
- [ ] Artifact Viewer renders HTML in sandboxed iframe
- [ ] Provider switching works via configuration
- [ ] Tests pass
- [ ] README instructions are complete and accurate

## 7. Risks & Trade-offs

| Risk | Mitigation |
|------|------------|
| Ollama may be slow on low-RAM machines | Recommend 8GB+ RAM; `llama3.2` is 3B params |
| 384-dim embeddings may miss nuance | Good enough for demo; can upgrade to 768-dim |
| Subset of transcripts limits coverage | Documented limitation; system handles gracefully |
| LLM may hallucinate | System prompt enforces grounding; empty retrieval → explicit refusal |
| HTML artifacts could be unsafe | Sandboxed iframe without allow-same-origin or allow-scripts |

## 8. Implementation Plan

See [architecture.md](./architecture.md) for technical details and [design.md](./design.md) for UI/UX.
