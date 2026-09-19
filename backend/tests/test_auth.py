from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_register_creates_user_and_returns_token(db_session):
    response = client.post(
        "/auth/register", json={"email": "new@example.com", "password": "supersecret123"}
    )

    assert response.status_code == 201
    body = response.json()
    assert body["user"]["email"] == "new@example.com"
    assert body["token_type"] == "bearer"
    assert body["access_token"]


def test_register_rejects_duplicate_email(db_session):
    client.post("/auth/register", json={"email": "dup@example.com", "password": "password123"})

    response = client.post(
        "/auth/register", json={"email": "dup@example.com", "password": "password456"}
    )

    assert response.status_code == 409


def test_register_rejects_short_password(db_session):
    response = client.post(
        "/auth/register", json={"email": "short@example.com", "password": "short"}
    )
    assert response.status_code == 422


def test_register_rejects_invalid_email(db_session):
    response = client.post(
        "/auth/register", json={"email": "not-an-email", "password": "password123"}
    )
    assert response.status_code == 422


def test_login_succeeds_with_correct_credentials(db_session):
    client.post("/auth/register", json={"email": "login@example.com", "password": "password123"})

    response = client.post(
        "/auth/login", json={"email": "login@example.com", "password": "password123"}
    )

    assert response.status_code == 200
    assert response.json()["access_token"]


def test_login_rejects_wrong_password(db_session):
    client.post("/auth/register", json={"email": "wrongpw@example.com", "password": "password123"})

    response = client.post(
        "/auth/login", json={"email": "wrongpw@example.com", "password": "notright"}
    )

    assert response.status_code == 401


def test_login_rejects_unknown_email(db_session):
    response = client.post(
        "/auth/login", json={"email": "doesnotexist@example.com", "password": "password123"}
    )
    assert response.status_code == 401


def test_me_returns_current_user(db_session, auth_headers):
    response = client.get("/auth/me", headers=auth_headers)

    assert response.status_code == 200
    assert "@" in response.json()["email"]


def test_me_rejects_missing_token(db_session):
    response = client.get("/auth/me")
    assert response.status_code == 401


def test_me_rejects_invalid_token(db_session):
    response = client.get("/auth/me", headers={"Authorization": "Bearer not-a-real-token"})
    assert response.status_code == 401
