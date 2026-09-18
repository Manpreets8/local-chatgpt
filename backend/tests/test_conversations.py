from fastapi.testclient import TestClient

from app.main import app
from app.services import llm_service as llm_service_module

client = TestClient(app)


def test_list_conversations_empty(db_session):
    response = client.get("/conversations")
    assert response.status_code == 200
    assert response.json() == []


def test_full_conversation_lifecycle(db_session, monkeypatch):
    monkeypatch.setattr(llm_service_module.llm_service, "chat", lambda messages: "a reply")

    chat_response = client.post("/chat", json={"message": "hi"})
    conversation_id = chat_response.json()["conversation_id"]

    list_response = client.get("/conversations")
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1

    detail_response = client.get(f"/conversations/{conversation_id}")
    assert detail_response.status_code == 200
    assert len(detail_response.json()["messages"]) == 2

    delete_response = client.delete(f"/conversations/{conversation_id}")
    assert delete_response.status_code == 204

    list_after_delete = client.get("/conversations")
    assert list_after_delete.json() == []


def test_get_missing_conversation_returns_404(db_session):
    response = client.get("/conversations/9999")
    assert response.status_code == 404


def test_delete_missing_conversation_returns_404(db_session):
    response = client.delete("/conversations/9999")
    assert response.status_code == 404
