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

- [x] UI polish: renamed app to "Local ChatGPT" (sidebar, tab title,
      FastAPI docs, README); redesigned as one cohesive dark theme
      (was a mismatched dark sidebar + white content) with a subtle
      gradient background and gradient accents on primary actions.

- [x] Chat attachments: a `+` button beside the message input supports
      two kinds of attachment. Images (PNG/JPEG/WEBP/GIF) are base64-
      encoded client-side and sent straight to Claude's vision
      capability for that turn only — not persisted as base64 in the
      DB (would bloat storage and get resent on every later turn), so
      the stored message text is a placeholder (`[Image attached]`)
      and image context doesn't carry into later turns. PDF/TXT/DOCX
      picked from the same button go through the existing document
      upload pipeline (Feature 3), with a toast-style notification
      confirming chunk count or failure. Backend validates image type/
      size and requires text-or-image (not neither). 37 backend tests
      passing; verified live with a real generated PNG (Claude
      correctly identified "solid red square") and a real doc upload,
      both through the actual browser UI via Playwright.

- [x] Feature 9: Auth — `users` table (Alembic migration), bcrypt password
      hashing (used directly, not via passlib — passlib 1.7.4 can't detect
      modern bcrypt 4.x as a backend and throws on its own self-test; a
      known, unmaintained-package compatibility bug, not a config mistake),
      JWT access tokens (python-jose). `POST /auth/register`,
      `POST /auth/login`, `GET /auth/me`. `conversations` and `documents`
      gained a `user_id` FK; every existing endpoint (`/chat`,
      `/conversations/*`, `/documents/*`) now requires a valid token via a
      `get_current_user` dependency, and every query is scoped to the
      caller — accessing another user's conversation/document by id
      returns 404 (not 403), so existence isn't leaked either.
      Frontend: a dedicated login/sign-up page (toggle between modes,
      matches the app's dark theme) gates the whole app; JWT stored in
      localStorage and attached to every request; a 401 anywhere logs the
      user out automatically (handles token expiry mid-session); sidebar
      shows the logged-in email with a Log out button.
      53 backend tests passing (up from 37), including cross-user
      isolation tests (user B gets 404 reading user A's conversation/
      document by id) and auth-required checks on every protected route.
      Verified live end to end via Playwright: sign up, chat while
      authenticated, log out, log back in, conversation history correctly
      persisted, and the session survives a full page reload. Also
      verified live via curl that a second real user cannot read a first
      user's conversation by guessing/reusing its id.

## Up Next

- [ ] Feature 4: RAG — embeddings (Sentence Transformers) + FAISS
      vector store + retrieval-augmented chat answers with source
      citations (document name + page number).
- [ ] Feature 6: Tool-using agent (calculator, doc search, db search, date/time).
- [ ] Feature 7: Resume analyzer.
- [ ] Feature 8: AI document summaries.
- [ ] Feature 10: Full dashboard UI (settings page, resume analyzer page).
- [ ] Feature 11: RAG evaluation.
- [ ] Docker Compose wiring for backend + frontend containers (Postgres
      is already containerized; backend/frontend still run via
      venv/npm locally).
- [ ] Known cosmetic gap: assistant replies containing Markdown (e.g.
      headings, bold, bullet lists) render as raw text, not formatted.

## Notes / Decisions

- LLM provider: Anthropic Claude API (chosen 2026-09-18).
- API keys: using `.env.example` placeholders; real key to be added by user
  before LLM-dependent features are tested live.
- Docker Desktop is not currently installed in this environment — Dockerfiles
  and docker-compose.yml are being written regardless, but Postgres-dependent
  features will need Docker (or a local Postgres install) to run/test.
