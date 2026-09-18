# Personal AI Agent — RAG + Memory + Tool-Using AI Assistant

A personal AI chatbot/agent built to demonstrate real AI/ML engineering: LLM
integration, conversation memory, document understanding (RAG), vector
search, tool calling, agentic workflows, authentication, and a production-style
full-stack architecture.

This project is being built incrementally, one feature at a time. See
[docs/PROGRESS.md](docs/PROGRESS.md) for what's done and what's next.

## Tech Stack

- **Backend:** Python 3.11, FastAPI, Pydantic, SQLAlchemy, PostgreSQL
- **AI/ML:** Anthropic Claude API, Sentence Transformers, FAISS (vector search,
  designed so pgvector can be swapped in later), scikit-learn
- **Document processing:** pypdf, python-docx (PDF/TXT/DOCX → text extraction
  → cleaning → chunking)
- **Frontend:** React, JavaScript
- **Infra:** Docker, Docker Compose, pytest

## Project Structure

```
personal-ai-agent/
├── backend/
│   ├── app/
│   │   ├── main.py       # FastAPI app entrypoint
│   │   ├── api/           # route handlers
│   │   ├── services/      # business logic (LLM calls, RAG, tools, etc.)
│   │   ├── models/        # SQLAlchemy ORM models
│   │   ├── schemas/       # Pydantic request/response schemas
│   │   ├── core/          # config, security
│   │   └── utils/
│   ├── tests/
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   └── src/
│       ├── components/
│       ├── pages/
│       └── services/
├── data/                  # uploaded documents, vector index (gitignored)
├── docs/
├── docker-compose.yml
├── .env.example
└── README.md
```

## Backend — Local Setup

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt

# from the project root, copy the env template and fill in real values
cp .env.example .env

uvicorn app.main:app --reload
```

Then visit:
- http://127.0.0.1:8000/health — liveness check
- http://127.0.0.1:8000/docs — interactive API docs (Swagger UI)

## Database (PostgreSQL via Docker)

```bash
docker compose up -d postgres
cd backend
alembic upgrade head
```

## Frontend — Local Setup

```bash
cd frontend
npm install

# copy the env template and point it at your backend
cp .env.example .env

npm run dev
```

Then visit http://localhost:5173 for the chat UI.

## Running Tests

```bash
cd backend
pytest -v
```

## Environment Variables

Copy `.env.example` to `.env` at the project root and fill in real secrets
(API keys, DB credentials, JWT secret). Never commit `.env`.

## Status

Currently implemented: project scaffolding + a health-check endpoint.
Everything else in the feature list (chat, memory, RAG, tools, resume
analyzer, auth, frontend, etc.) is being added incrementally — see
[docs/PROGRESS.md](docs/PROGRESS.md).
