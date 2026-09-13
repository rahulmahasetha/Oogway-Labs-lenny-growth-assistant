# Lenny Growth Assistant

An AI-powered product management assistant grounded in Lenny's Podcast transcripts and newsletters. Built as a Forward Deployed Engineer take-home assignment.

<p align="center">
  <img src="assets/welcome-screen.png" alt="Welcome Screen" width="800"/>
</p>

## Screenshots

<details>
<summary><b>View Application Screenshots</b></summary>
<br/>

**RAG-Powered Q&A**
<img src="assets/chat-qa.png" alt="Q&A Chat" width="800"/>

**Ship 30 for 30 Essay Generation**
<img src="assets/essay-generation.png" alt="Essay Generation" width="800"/>

**HTML Document Generation (Sandboxed Viewer)**
<img src="assets/html-artifact.png" alt="HTML Artifact" width="800"/>

</details>

## Features

- 💬 **RAG-Powered Q&A** — Answers product management and growth questions using 50 podcast transcripts and 10 newsletter articles
- 📝 **Ship 30 for 30 Essays** — Generates ~1,250-word publication-ready essays grounded in transcript knowledge
- 📄 **Artifact Viewer** — Renders Markdown and HTML artifacts in a side panel with security sandboxing
- 🔗 **Source Citations** — Every response includes clickable links to source episodes
- 🔄 **Multi-Session Chat** — Independent conversations with PostgreSQL persistence
- 🤖 **Model Switching** — Supports Ollama (local), OpenAI, and Anthropic via configuration
- 🐳 **Docker Compose** — One-command deployment

## Architecture

```mermaid
graph TD
    subgraph Client ["Frontend"]
        UI[React + Vite UI]
        Viewer[Artifact Viewer]
    end
    
    subgraph Server ["Backend (FastAPI)"]
        API[API Router]
        Agent[Agent Orchestrator]
        RAG[RAG Retrieval]
        Provider[LLM Provider Factory]
    end
    
    subgraph Data ["Data Layer"]
        DB[(PostgreSQL + pgvector)]
    end
    
    subgraph Models ["LLM Models"]
        Ollama[Ollama Local]
        OpenAI[OpenAI Cloud]
        Anthropic[Anthropic Cloud]
    end

    UI <-->|REST API| API
    Viewer --- UI
    
    API <--> Agent
    Agent <--> RAG
    RAG <-->|SQL/Vector Search| DB
    Agent <--> Provider
    
    Provider -.- Ollama
    Provider -.- OpenAI
    Provider -.- Anthropic

    style Client fill:#e6f3ff,stroke:#0066cc,stroke-width:2px,color:#333
    style Server fill:#f0f7f0,stroke:#2ca02c,stroke-width:2px,color:#333
    style Data fill:#fff2e6,stroke:#ff7f0e,stroke-width:2px,color:#333
    style Models fill:#f4e6ff,stroke:#9467bd,stroke-width:2px,color:#333
```

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and Docker Compose
- [Ollama](https://ollama.ai/) (for local model) — install from https://ollama.ai/
- (Optional) OpenAI or Anthropic API key for cloud models

## Quick Start

### 1. Clone and configure

```bash
git clone <repo-url>
cd lenny-growth-assistant
cp .env.example .env
```

### 2. Start Ollama (local model)

```bash
# Install Ollama from https://ollama.ai/
ollama serve              # Start the Ollama server
ollama pull llama3.2      # Download the default model (~2GB)
```

### 3. Start the application

```bash
docker compose up --build
```

This starts:
- PostgreSQL (with pgvector) on port 5432
- Backend (FastAPI) on port 8000
- Frontend (React + Vite) on port 5173

### 4. Run database migrations

The first time, run migrations to create the schema:

```bash
docker compose exec backend python -m alembic upgrade head
```

### 5. Ingest transcripts

Ingest the 60 transcript files into the database:

```bash
curl -X POST http://localhost:8000/api/ingestion/run
```

Or click the "Ingest Transcripts" button in the sidebar.

### 6. Use the app

Open [http://localhost:5173](http://localhost:5173) in your browser.

- Click "New Chat" to start a conversation
- Ask questions like "How did Duolingo reignite user growth?"
- Request essays: "Write an essay about how AI is changing product teams"
- Click source citations to see original episodes

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `LLM_PROVIDER` | `ollama` | Active provider: `ollama`, `openai`, or `anthropic` |
| `OLLAMA_BASE_URL` | `http://host.docker.internal:11434` | Ollama API URL |
| `OLLAMA_MODEL` | `llama3.2` | Ollama model name |
| `OPENAI_API_KEY` | (empty) | OpenAI API key (required if provider=openai) |
| `OPENAI_MODEL` | `gpt-4o-mini` | OpenAI model |
| `ANTHROPIC_API_KEY` | (empty) | Anthropic API key (required if provider=anthropic) |
| `ANTHROPIC_MODEL` | `claude-sonnet-4-20250514` | Anthropic model |
| `POSTGRES_USER` | `lenny` | PostgreSQL username |
| `POSTGRES_PASSWORD` | `lenny_secret` | PostgreSQL password |
| `POSTGRES_DB` | `lenny_growth` | PostgreSQL database name |
| `RAG_TOP_K` | `8` | Number of chunks to retrieve |
| `RAG_SIMILARITY_THRESHOLD` | `0.35` | Minimum cosine similarity |

## Using Cloud Models

### OpenAI

```bash
# In .env:
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4o-mini
```

### Anthropic

```bash
# In .env:
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-your-key-here
ANTHROPIC_MODEL=claude-sonnet-4-20250514
```

Restart the backend after changing providers:
```bash
docker compose restart backend
```

## Local Development (without Docker)

### Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Start PostgreSQL (e.g., via Docker)
docker run -d --name lenny-pg -e POSTGRES_USER=lenny -e POSTGRES_PASSWORD=lenny_secret -e POSTGRES_DB=lenny_growth -p 5432:5432 pgvector/pgvector:pg16

# Set env vars
export DATABASE_URL=postgresql+asyncpg://lenny:lenny_secret@localhost:5432/lenny_growth
export DATA_DIR=../data

# Run migrations
python -m alembic upgrade head

# Start backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Testing

### Backend tests

```bash
cd backend
source .venv/bin/activate
python -m pytest -v
```

### Frontend build check

```bash
cd frontend
npx tsc --noEmit
```

## Project Structure

```
lenny-growth-assistant/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application
│   │   ├── config.py            # Environment configuration
│   │   ├── database.py          # SQLAlchemy async setup
│   │   ├── models.py            # ORM models
│   │   ├── schemas.py           # Pydantic schemas
│   │   ├── routers/             # API endpoints
│   │   └── services/            # Business logic
│   │       ├── agent.py         # Chat orchestrator
│   │       ├── rag.py           # Retrieval service
│   │       ├── ingestion.py     # Transcript ingestion
│   │       ├── ship30.py        # Essay generation skill
│   │       ├── artifacts.py     # Artifact generation
│   │       └── llm/             # Provider abstraction
│   ├── alembic/                 # Database migrations
│   └── tests/                   # Pytest tests
├── frontend/
│   └── src/
│       ├── App.tsx              # Main application
│       ├── api/client.ts        # API client
│       └── components/          # React components
├── data/
│   ├── podcasts/                # 50 podcast transcripts
│   └── newsletters/             # 10 newsletter articles
├── docs/
│   ├── PRD.md                   # Product requirements
│   ├── design.md                # UI/UX design
│   ├── architecture.md          # Technical architecture
│   └── test-plan.md             # Manual test plan
├── agent-transcripts/           # Coding agent interactions
├── docker-compose.yml
├── .env.example
├── Makefile
└── README.md
```

## API Documentation

The backend serves an interactive API documentation page at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Troubleshooting

### Ollama connection issues
```bash
# Ensure Ollama is running
ollama serve

# Check from Docker
curl http://host.docker.internal:11434/api/tags

# For Linux, you may need to set:
OLLAMA_BASE_URL=http://172.17.0.1:11434
```

### Database connection issues
```bash
# Check PostgreSQL is running
docker compose ps postgres

# Check logs
docker compose logs postgres

# Reset database
docker compose down -v
docker compose up -d postgres
```

### Ingestion issues
```bash
# Check ingestion status
curl http://localhost:8000/api/ingestion/status

# Re-run ingestion (idempotent — skips already-ingested files)
curl -X POST http://localhost:8000/api/ingestion/run
```

### Model loading slow
First-time model loading can take 30-60 seconds. Subsequent requests are faster. If using Ollama, ensure you've pulled the model first: `ollama pull llama3.2`

## Known Limitations

1. **Dataset subset**: Only 50/200+ podcast episodes and 10/hundreds of newsletter articles are included. Some topics may not have coverage.
2. **Embedding model**: Uses `all-MiniLM-L6-v2` (384-dim) for speed. Production could upgrade to a larger model for better retrieval.
3. **No authentication**: Single-user demo. Production would need auth.
4. **No streaming**: Responses are returned as a single block. Streaming would improve UX for long responses.
5. **Ollama dependency**: Local demo requires Ollama running on the host. Docker networking to host can vary by OS.

## Documentation

- [Product Requirements (PRD)](docs/PRD.md)
- [Design Document](docs/design.md)
- [Architecture Document](docs/architecture.md)
- [Manual Test Plan](docs/test-plan.md)
