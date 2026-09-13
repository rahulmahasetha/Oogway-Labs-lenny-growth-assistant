# Manual UI Test Plan

## Setup
1. Start the application: `docker compose up --build`
2. Run migrations: `docker compose exec backend python -m alembic upgrade head`
3. Ingest transcripts: Click "Ingest Transcripts" in sidebar
4. Open http://localhost:5173

## Test Cases

### 1. Health Check
- [ ] Visit http://localhost:8000/health
- [ ] Verify response shows `status: "healthy"`, `database: "healthy"`
- [ ] Verify Ollama status reflects whether it's running

### 2. Session Management
- [ ] Click "New Chat" → new session appears in sidebar
- [ ] Create 3+ sessions → all appear in sidebar, newest first
- [ ] Click different sessions → chat area switches
- [ ] Delete a session → removed from sidebar, no data leakage

### 3. Chat — Basic Q&A
- [ ] Ask: "How did Duolingo reignite user growth?"
- [ ] Verify response references Jorge Mazal and specific growth strategies
- [ ] Verify source citations appear below the response
- [ ] Click a source citation → opens in new tab (if URL available)

### 4. Chat — Session Isolation
- [ ] In Session A, ask about Duolingo
- [ ] Create Session B, ask about AI coding agents
- [ ] Switch back to Session A → history only shows Duolingo question
- [ ] Verify Session B → history only shows AI coding question

### 5. Chat — Follow-up Questions
- [ ] Ask: "What does Adam Mosseri think about product teams?"
- [ ] Follow up: "What about the pods he mentioned?"
- [ ] Verify follow-up uses session context and gives relevant response

### 6. Chat — No Relevant Content
- [ ] Ask: "What's the best pizza in New York?"
- [ ] Verify response explicitly states the transcripts don't cover this topic
- [ ] Verify no fabricated sources appear

### 7. Essay Generation
- [ ] Ask: "Write an essay about how AI is changing product development"
- [ ] Verify response mentions the Artifact Viewer
- [ ] Click "View Artifact" button → artifact panel opens
- [ ] Verify essay is ~1,250 words with headings, bold, and source attributions
- [ ] Verify sources section at end of essay

### 8. Artifact Viewer
- [ ] Verify empty state shows when no artifact exists
- [ ] Verify Markdown artifact renders with proper formatting
- [ ] Request: "Create a styled HTML document about growth strategies"
- [ ] Verify HTML artifact renders in sandboxed iframe
- [ ] Verify close button dismisses the panel

### 9. Artifact Security
- [ ] In HTML artifact, verify no JavaScript executes
- [ ] Verify iframe does not have access to parent window
- [ ] Inspect iframe element → confirm `sandbox=""` attribute

### 10. Provider Badge
- [ ] Check sidebar footer shows current provider and model
- [ ] Verify it reflects the `LLM_PROVIDER` environment variable

### 11. Responsive Layout
- [ ] Resize to <768px → mobile layout activates
- [ ] Click hamburger menu → sidebar appears as overlay
- [ ] Select a session → sidebar closes, chat appears
- [ ] Verify artifact viewer works on mobile

### 12. Loading & Error States
- [ ] Send a message → loading dots appear while waiting
- [ ] Verify user message appears immediately (optimistic update)
- [ ] Stop Ollama → send message → verify error is displayed gracefully

### 13. Keyboard Navigation
- [ ] Tab through sidebar sessions → focus is visible
- [ ] Press Enter on a session → selects it
- [ ] In composer: Enter sends, Shift+Enter adds newline
- [ ] Tab to send button → Enter sends

### 14. Ingestion
- [ ] Click "Ingest Transcripts" → button shows loading
- [ ] Visit http://localhost:8000/api/ingestion/status
- [ ] Verify: 50 podcasts + 10 newsletters = 60 sources
- [ ] Click "Ingest Transcripts" again → verify skipped count (idempotent)
