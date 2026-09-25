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

- [x] AI image generation — a "🎨 Generate Image" composer mode (toggle
      next to the message input, alongside "💬 Chat") generates a new
      image from a text prompt via Pollinations.ai's free, keyless
      `sana` model. Started as "edit an uploaded photo" per the user's
      request, but every provider tested gates actual photo-editing
      behind billing:
        - OpenAI gpt-image-1: no free tier at all.
        - Google Gemini image model: free-tier quota is 0 for image
          generation specifically (confirmed live — a valid, working
          key still gets `RESOURCE_EXHAUSTED`), despite Gemini's text
          models having a real free tier.
        - Pollinations.ai's image-editing model ("kontext") now requires
          their own paid tier too.
      Pure text-to-image generation (no input photo) is the one thing
      that's actually free everywhere tested, so the feature was
      rescoped to that rather than silently shipping something that
      only works with a paid key. Known limitation: Pollinations' free
      tier stamps a small watermark on results even with `nologo=true`
      requested — removing it isn't available for free either.
      Backend: `generated_images` table (prompt, content_type) plus a
      nullable `generated_image_id` FK on `messages`, so generated
      images live in real conversation history (not a side flow) and
      reload correctly later — `GET /images/{id}` streams the bytes,
      ownership-checked like every other resource. 62 backend tests
      passing. Verified live: a real generated image (a 3D-Pixar-style
      baby dragon) through the actual browser via Playwright, confirmed
      it persists correctly after a full page reload and reopening the
      conversation.

- [x] Deployed to production — Vercel (frontend), Render (backend,
      Docker-based, migrations run automatically on every deploy),
      Neon (Postgres). All free tiers, no cards required. Verified
      live end to end via Playwright against the real public URLs
      (sign up, real Claude chat, mobile layout), not just localhost.
      Two real bugs found and fixed along the way, both general
      hardening, not one-off patches: (1) Render's "Docker Command"
      field had the Dockerfile *path* typed into it by mistake,
      overriding the image's own CMD and crashing every deploy
      instantly; (2) the Anthropic key picked up an invisible trailing
      newline when pasted into Render's dashboard, which httpx
      correctly refused to send as a header value — fixed by having
      `Settings` strip whitespace from every string field on load, so
      this can't recur regardless of which platform or paste path a
      secret goes through. Known constraint: free tier means the
      backend spins down after ~15 min idle and takes 30-60s to wake
      on the next request — expected, not a bug.

- [x] Image generation quality pass — tested three levers live
      against the free Pollinations model before changing anything:
      explicit width/height (was requesting none at all before, so
      resolution was whatever the default happened to be), `enhance`
      (Pollinations' own prompt-rewriting), and style-keyword
      reinforcement. Finding, confirmed by direct comparison images:
      the free `sana` model has a hard photorealism bias for
      landscape/wide scenes that not even an explicit negative prompt
      overrides — a real ceiling of the free model, not a prompting
      problem. It does follow explicit style/material keywords well
      for single-subject/character prompts. Shipped the parts that
      measurably help: 1024x1024 requests, `enhance=true` always, and
      automatic style-boost keywords added only when the user's own
      prompt already signals 3D/animated/cartoon intent (never forced
      onto prompts that don't ask for it). 5 new unit tests, 67
      backend tests passing total.

- [x] Welcome email on signup — sent via Gmail SMTP (stdlib `smtplib`,
      no third-party SDK) as a non-blocking FastAPI `BackgroundTask`,
      so a slow/flaky mail server can never delay or break signup.
      Started with Resend (a proper transactional email API) but
      discovered live that its free/unverified-domain tier can only
      send to the account's own address — every other recipient gets
      a 403, which would mean the feature only worked for the
      developer's own test account, not real users. Switched to Gmail
      SMTP instead, confirmed live it has no such restriction (sent
      successfully to a second, unrelated address). Needs a Gmail
      App Password (requires 2-Step Verification), not the account's
      normal password. Also fixed a real test-suite bug found in the
      process: registration's background email task was making *real*
      SMTP connections during every auth test once real credentials
      landed in `.env`, silently making the suite minutes slower —
      added an autouse fixture that stubs the real send for every test
      except `test_email_service.py`'s own, which mocks `smtplib`
      directly and needs the real method. 71 backend tests passing.

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
