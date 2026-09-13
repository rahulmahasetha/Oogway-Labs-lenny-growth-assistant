# Architecture Document — Lenny Growth Assistant

## 1. System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Docker Compose                           │
│                                                                  │
│  ┌────────────┐    ┌──────────────────┐    ┌────────────────┐   │
│  │  Frontend   │    │     Backend      │    │   PostgreSQL   │   │
│  │  React+Vite │───▶│     FastAPI      │───▶│  + pgvector    │   │
│  │  :5173      │    │     :8000        │    │  :5432         │   │
│  └────────────┘    └────────┬─────────┘    └────────────────┘   │
│                             │                                     │
│                    ┌────────┴────────┐                           │
│                    │   LLM Provider   │                          │
│                    │   (pluggable)    │                          │
│                    ├─────────────────┤                           │
│                    │  Ollama (local)  │                          │
│                    │  OpenAI (cloud)  │                          │
│                    │  Anthropic (cloud)│                         │
│                    └─────────────────┘                           │
└─────────────────────────────────────────────────────────────────┘
```

## 2. Database Schema

### Sources
| Column | Type | Description |
|--------|------|-------------|
| id | UUID (PK) | Unique identifier |
| title | TEXT | Episode/article title |
| source_type | VARCHAR(20) | 'podcast' or 'newsletter' |
| guest | VARCHAR(255) | Podcast guest name |
| date | DATETIME | Publication date |
| post_url | TEXT | Substack URL |
| youtube_url | TEXT | YouTube URL (some podcasts) |
| description | TEXT | Episode description |
| word_count | INTEGER | Word count |
| file_path | TEXT (UNIQUE) | Relative file path (prevents duplicates) |
| created_at | TIMESTAMPTZ | Ingestion timestamp |

### Chunks
| Column | Type | Description |
|--------|------|-------------|
| id | UUID (PK) | Unique identifier |
| source_id | UUID (FK→sources) | Parent source |
| content | TEXT | Chunk text content |
| chunk_index | INTEGER | Position in source |
| speaker | VARCHAR(255) | Speaker name (podcasts) |
| start_time | VARCHAR(20) | Timestamp (podcasts) |
| embedding | VECTOR(384) | pgvector embedding |
| created_at | TIMESTAMPTZ | Ingestion timestamp |

### Sessions
| Column | Type | Description |
|--------|------|-------------|
| id | UUID (PK) | Session identifier |
| title | VARCHAR(255) | Auto-set from first message |
| created_at | TIMESTAMPTZ | Creation time |
| updated_at | TIMESTAMPTZ | Last activity |

### Messages
| Column | Type | Description |
|--------|------|-------------|
| id | UUID (PK) | Message identifier |
| session_id | UUID (FK→sessions) | Parent session |
| role | VARCHAR(20) | 'user' or 'assistant' |
| content | TEXT | Message text |
| sources | JSONB | Cited source references |
| artifact | JSONB | Generated artifact {type, content, title} |
| created_at | TIMESTAMPTZ | Creation timestamp |

### Indexes
- `idx_chunks_source` on chunks(source_id)
- `idx_messages_session_created` on messages(session_id, created_at)
- pgvector IVFFlat index on chunks(embedding) for cosine similarity

## 3. API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check (DB + Ollama status) |
| POST | `/api/sessions` | Create new chat session |
| GET | `/api/sessions` | List all sessions (newest first) |
| GET | `/api/sessions/{id}` | Get session with message history |
| DELETE | `/api/sessions/{id}` | Delete session and messages |
| POST | `/api/sessions/{id}/messages` | Send message, receive AI response |
| POST | `/api/ingestion/run` | Trigger transcript ingestion |
| GET | `/api/ingestion/status` | Get ingestion statistics |
| GET | `/api/sources/{id}` | Get source details |
| GET | `/api/config` | Get active provider/model config |

## 4. Component Boundaries

### Backend Components

```
app/
├── main.py            → FastAPI app factory, CORS, lifespan
├── config.py          → Pydantic Settings (env-driven)
├── database.py        → SQLAlchemy async engine + session
├── models.py          → ORM models (Source, Chunk, Session, Message)
├── schemas.py         → Pydantic request/response schemas
├── routers/           → API endpoint handlers
│   ├── health.py      → Health check
│   ├── sessions.py    → Session CRUD
│   ├── messages.py    → Message handling (core chat flow)
│   ├── ingestion.py   → Ingestion trigger + status
│   ├── sources.py     → Source details
│   └── config.py      → Active configuration
├── services/          → Business logic
│   ├── agent.py       → Chat orchestrator (routing, RAG, LLM)
│   ├── rag.py         → Retrieval: embed query → pgvector search
│   ├── ingestion.py   → Parse, chunk, embed, store transcripts
│   ├── ship30.py      → Ship 30 for 30 essay skill
│   ├── artifacts.py   → Artifact generation (MD/HTML)
│   └── llm/           → Provider abstraction
│       ├── base.py    → Abstract interface
│       ├── ollama.py  → Ollama HTTP client
│       ├── openai_provider.py  → OpenAI SDK wrapper
│       ├── anthropic_provider.py → Anthropic SDK wrapper
│       └── factory.py → Provider factory (singleton)
└── utils/
    ├── logging.py     → Structured logging (structlog)
    └── errors.py      → Error classes + FastAPI handlers
```

### Frontend Components
```
src/
├── App.tsx              → Main orchestrator (React Query, state)
├── api/client.ts        → Typed API client
├── types/index.ts       → TypeScript interfaces
└── components/
    ├── Sidebar.tsx       → Session list, new chat, provider badge
    ├── ChatArea.tsx      → Messages, starter prompts, welcome
    ├── MessageBubble.tsx → Message with markdown + citations
    ├── MessageComposer.tsx → Input with auto-resize
    └── ArtifactViewer.tsx  → MD/HTML viewer (sandboxed)
```

## 5. Ingestion & Retrieval Flow

### Ingestion Pipeline
```
data/podcasts/*.md + data/newsletters/*.md
        │
        ▼
  Parse YAML frontmatter → metadata (title, guest, date, URLs)
        │
        ▼
  Chunk content:
    - Podcasts: by speaker turns, ~2000 chars, 200 overlap
    - Newsletters: by sections/headings, ~2000 chars, 200 overlap
        │
        ▼
  Generate embeddings (sentence-transformers/all-MiniLM-L6-v2, 384-dim)
        │
        ▼
  Store in PostgreSQL:
    - Source record (metadata + file_path UNIQUE constraint)
    - Chunk records (content + embedding)
```

### Retrieval Flow
```
User query
    │
    ▼
Embed query with same model (all-MiniLM-L6-v2)
    │
    ▼
pgvector cosine similarity search (top-k=8, threshold=0.35)
    │
    ▼
De-duplicate by source
    │
    ▼
Build attributed context string
    │
    ▼
Pass to LLM with system prompt + context
```

### Chunking Details
- **Target size**: ~2000 characters per chunk
- **Overlap**: 200 characters between chunks
- **Podcast strategy**: Split at speaker turn boundaries when possible
- **Newsletter strategy**: Split at heading boundaries, then paragraphs
- **Metadata preservation**: Each chunk retains source_id, speaker, timestamp

### Retrieval Parameters
- **Embedding model**: `all-MiniLM-L6-v2` (384 dimensions, free, fast)
- **Top-k**: 8 chunks retrieved per query
- **Similarity threshold**: 0.35 (cosine similarity)
- **Index**: IVFFlat on embedding column

## 6. Agent Routing

```
User message
    │
    ▼
Is essay request? ──yes──▶ Ship 30 for 30 skill
    │ no                        │
    ▼                           ▼
Is artifact request? ──yes──▶ Artifact generation
    │ no                        │
    ▼                           ▼
Regular Q&A ──────────────▶ Grounded response
    │
    ▼
All paths:
  1. Retrieve RAG context
  2. Generate response
  3. Build source citations
  4. Return content + sources + artifact (if any)
```

Detection uses regex keyword matching:
- **Essay**: "essay", "ship 30", "write an article", "deep dive", "long-form"
- **Artifact**: "create a document", "generate a report", "HTML document"

## 7. Model Toggle

The LLM layer uses a provider abstraction pattern:

1. `LLMProvider` abstract base class defines the interface
2. `OllamaProvider`, `OpenAIProvider`, `AnthropicProvider` implement it
3. `get_llm_provider()` factory selects based on `LLM_PROVIDER` env var
4. Provider is a singleton (reset available for testing)

Switching providers requires changing one env var:
```bash
LLM_PROVIDER=openai    # or "ollama" or "anthropic"
```

## 8. Security Strategy

### Artifact Viewer
- **Markdown**: Rendered in-app with `react-markdown` + `remark-gfm` (no raw HTML pass-through)
- **HTML**: Rendered in sandboxed iframe with these restrictions:
  - `sandbox=""` attribute (maximum restriction)
  - No `allow-same-origin` → iframe cannot access parent's DOM, cookies, or localStorage
  - No `allow-scripts` → JavaScript is completely blocked
  - Content via `srcdoc` → no network request to load
- **LLM prompt**: HTML artifact generation prompt explicitly forbids JavaScript

### API Security
- CORS configured (currently permissive for demo; production would restrict origins)
- Input validation via Pydantic (max message length: 10,000 chars)
- Structured error responses (no stack traces in production)
- No secrets committed (env vars via `.env`)

### Database
- Parameterized queries via SQLAlchemy (SQL injection prevention)
- Session isolation via UUID foreign keys
- Cascade deletes for data consistency

## 9. Deployment Topology

```yaml
# docker-compose.yml
services:
  postgres:     # pgvector/pgvector:pg16, port 5432, health-checked
  backend:      # Python 3.12, port 8000, depends on postgres
  frontend:     # Node 20, port 5173, depends on backend
```

- PostgreSQL uses a named volume for persistence
- Backend mounts `data/` read-only for transcript access
- Backend uses `host.docker.internal` to reach host Ollama
- Frontend proxies API requests to backend

### Local Development (without Docker)
1. Start PostgreSQL (local or Docker)
2. `cd backend && source .venv/bin/activate && uvicorn app.main:app --reload`
3. `cd frontend && npm run dev`
4. Start Ollama: `ollama serve` + `ollama pull llama3.2`
