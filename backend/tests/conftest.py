import itertools

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.main import app

_email_counter = itertools.count(1)


@pytest.fixture(autouse=True)
def _no_real_emails(request, monkeypatch):
    """Safety net for every test, not just email-specific ones:
    registration triggers a background task that sends a real welcome
    email using whatever SMTP credentials happen to be in the ambient
    .env file. Without this, the whole suite would attempt real SMTP
    connections on every registration test, regardless of which file
    is running or whether it's about email at all.

    Excludes test_email_service.py, which needs the real method to
    test it (and already mocks smtplib itself, so it's still safe)."""
    if request.module.__name__.endswith("test_email_service"):
        return
    monkeypatch.setattr(
        "app.services.email_service.email_service.send_welcome_email",
        lambda to_email: None,
    )


@pytest.fixture()
def db_session():
    """In-memory SQLite so DB-backed tests run without Docker/Postgres.
    Same schema, no real infra needed for a fast test suite."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    testing_session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = testing_session_local()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    yield testing_session_local
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def auth_headers(db_session):
    """Registers a fresh test user and returns an Authorization header
    for it. Most endpoints now require auth, so this is the standard
    way tests act as a logged-in user."""
    client = TestClient(app)
    email = f"user{next(_email_counter)}@example.com"
    response = client.post(
        "/auth/register", json={"email": email, "password": "testpassword123"}
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
