# Build Progress

Tracking features from the spec as they're built, one at a time.

## Done

- [x] Project scaffolding — folder structure, git, FastAPI skeleton,
      `/health` endpoint, pytest set up and passing, Dockerfile for backend.
- [x] Feature 1 (backend half): `POST /chat` single-turn endpoint calling
      the Claude API via `LLMService` (`app/services/llm_service.py`).
      Handles missing API key (503) and API errors (502) cleanly. 4 tests
      passing, verified live with curl and a real API key/billing.
- [x] Feature 1 (frontend half): React + Vite chat UI (`frontend/src`) —
      message bubbles, timestamps, loading indicator (typing dots), error
      display, New Chat (clears in-memory state), responsive down to
      mobile width. Verified live with Playwright: real user message sent,
      real Claude reply rendered, screenshots checked on desktop + mobile.
      No persistence yet — that's Feature 2 (conversation memory in
      PostgreSQL), so "New Chat" and history are still local-only.

- [x] Feature 2: Conversation memory — Postgres via Docker Compose,
      SQLAlchemy models (`conversations`, `messages`), Alembic migrations,
      `/chat` now persists history and replies with full context,
      `GET/DELETE /conversations` endpoints. Frontend: sidebar with real
      conversation list, click to reload history, delete, auto-derived
      titles, collapsible drawer on mobile. Verified live: the exact
      "My name is Manpreet" → "What is my name?" example from the spec
      works correctly end to end (confirmed via direct DB inspection and
      Playwright), plus New Chat, multi-conversation switching, delete,
      and the mobile drawer. 11 backend tests passing (SQLite-backed, no
      Docker needed to run the suite).
      Known cosmetic gap: assistant replies containing Markdown (e.g.
      headings, bold, bullet lists) render as raw text, not formatted —
      candidate for a small follow-up, not blocking.

- [x] Feature 3: Document upload — `documents` / `document_chunks` tables
      (Alembic migration), extraction (pypdf for PDF, python-docx for
      DOCX, plain decode for TXT) → cleaning → chunking (800 chars,
      100 overlap, page numbers preserved for PDFs). `POST
      /documents/upload` validates type (PDF/TXT/DOCX only) and size
      (10MB max), processes synchronously, and marks status
      ready/failed (e.g. empty/unextractable content) rather than
      crashing on bad input. `GET/DELETE /documents` for listing and
      removal (also deletes the file from `data/uploads/`). Frontend:
      new Documents page (sidebar nav: Chat / Documents) with upload
      button, status badges, chunk counts, delete — responsive with
      horizontal scroll on mobile. 33 backend tests passing, including
      a real generated PDF with actual extractable text (not mocked)
      and a real DOCX built with python-docx. Verified live via
      Playwright: upload PDF, upload TXT, delete, mobile layout.
      No embeddings/vector storage yet — deliberately split off as
      Feature 4 (RAG) rather than bundled in, so each feature stays
      independently testable.

## Up Next

- [ ] Feature 4: RAG — embeddings (Sentence Transformers) + FAISS
      vector store + retrieval-augmented chat answers with source
      citations (document name + page number) — PostgreSQL + Docker Compose,
      conversations/messages tables, multi-turn context.
- [ ] Feature 3: Document upload — extraction, cleaning, chunking pipeline.
- [ ] Feature 4: Embeddings + FAISS vector store.
- [ ] Feature 5: RAG — retrieval-augmented answers with source citations.
- [ ] Feature 6: Tool-using agent (calculator, doc search, db search, date/time).
- [ ] Feature 7: Resume analyzer.
- [ ] Feature 8: AI document summaries.
- [ ] Feature 9: Auth (register/login, JWT, password hashing).
- [ ] Feature 10: Full dashboard UI (sidebar, documents page, resume analyzer page).
- [ ] Feature 11: RAG evaluation.
- [ ] Docker Compose wiring for backend + frontend + Postgres.

## Notes / Decisions

- LLM provider: Anthropic Claude API (chosen 2026-09-18).
- API keys: using `.env.example` placeholders; real key to be added by user
  before LLM-dependent features are tested live.
- Docker Desktop is not currently installed in this environment — Dockerfiles
  and docker-compose.yml are being written regardless, but Postgres-dependent
  features will need Docker (or a local Postgres install) to run/test.
