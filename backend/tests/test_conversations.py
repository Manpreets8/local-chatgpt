from fastapi.testclient import TestClient

from app.main import app
from app.services import llm_service as llm_service_module

client = TestClient(app)


def test_list_conversations_requires_auth(db_session):
    response = client.get("/conversations")
    assert response.status_code == 401


def test_list_conversations_empty(db_session, auth_headers):
    response = client.get("/conversations", headers=auth_headers)
    assert response.status_code == 200
    assert response.json() == []


def test_full_conversation_lifecycle(db_session, auth_headers, monkeypatch):
    monkeypatch.setattr(llm_service_module.llm_service, "chat", lambda messages: "a reply")

    chat_response = client.post("/chat", json={"message": "hi"}, headers=auth_headers)
    conversation_id = chat_response.json()["conversation_id"]

    list_response = client.get("/conversations", headers=auth_headers)
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1

    detail_response = client.get(f"/conversations/{conversation_id}", headers=auth_headers)
    assert detail_response.status_code == 200
    assert len(detail_response.json()["messages"]) == 2

    delete_response = client.delete(f"/conversations/{conversation_id}", headers=auth_headers)
    assert delete_response.status_code == 204

    list_after_delete = client.get("/conversations", headers=auth_headers)
    assert list_after_delete.json() == []


def test_get_missing_conversation_returns_404(db_session, auth_headers):
    response = client.get("/conversations/9999", headers=auth_headers)
    assert response.status_code == 404


def test_delete_missing_conversation_returns_404(db_session, auth_headers):
    response = client.delete("/conversations/9999", headers=auth_headers)
    assert response.status_code == 404


def test_conversations_are_isolated_between_users(db_session, auth_headers, monkeypatch):
    monkeypatch.setattr(llm_service_module.llm_service, "chat", lambda messages: "a reply")

    client.post("/chat", json={"message": "user one's chat"}, headers=auth_headers)

    other = client.post(
        "/auth/register", json={"email": "other-conv@example.com", "password": "password123"}
    )
    other_headers = {"Authorization": f"Bearer {other.json()['access_token']}"}

    response = client.get("/conversations", headers=other_headers)
    assert response.status_code == 200
    assert response.json() == []
