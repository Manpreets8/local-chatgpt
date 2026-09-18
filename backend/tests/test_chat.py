from fastapi.testclient import TestClient

from app.main import app
from app.services import llm_service as llm_service_module

client = TestClient(app)


def test_chat_returns_reply_from_llm_service(monkeypatch):
    monkeypatch.setattr(
        llm_service_module.llm_service, "chat", lambda message: f"echo: {message}"
    )

    response = client.post("/chat", json={"message": "hello"})

    assert response.status_code == 200
    assert response.json() == {"reply": "echo: hello"}


def test_chat_rejects_empty_message():
    response = client.post("/chat", json={"message": ""})

    assert response.status_code == 422


def test_chat_returns_503_when_llm_not_configured(monkeypatch):
    def raise_not_configured(message):
        raise llm_service_module.LLMNotConfiguredError("not configured")

    monkeypatch.setattr(llm_service_module.llm_service, "chat", raise_not_configured)

    response = client.post("/chat", json={"message": "hello"})

    assert response.status_code == 503
