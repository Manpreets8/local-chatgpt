# Build Progress

Tracking features from the spec as they're built, one at a time.

## Done

- [x] Project scaffolding — folder structure, git, FastAPI skeleton,
      `/health` endpoint, pytest set up and passing, Dockerfile for backend.
- [x] Feature 1 (backend half): `POST /chat` single-turn endpoint calling
      the Claude API via `LLMService` (`app/services/llm_service.py`).
      Handles missing API key (503) and API errors (502) cleanly. 4 tests
      passing, verified live with curl. Frontend chat UI still to do.

## Up Next

- [ ] Feature 1 (frontend half): minimal React chat UI wired to `POST /chat`.
- [ ] Feature 2: Conversation memory — PostgreSQL + Docker Compose,
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
