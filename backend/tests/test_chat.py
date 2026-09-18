from fastapi.testclient import TestClient

from app.main import app
from app.services import llm_service as llm_service_module

client = TestClient(app)


def test_chat_creates_conversation_and_returns_reply(db_session, monkeypatch):
    monkeypatch.setattr(
        llm_service_module.llm_service,
        "chat",
        lambda messages: f"echo: {messages[-1]['content']}",
    )

    response = client.post("/chat", json={"message": "hello"})

    assert response.status_code == 200
    body = response.json()
    assert body["reply"] == "echo: hello"
    assert isinstance(body["conversation_id"], int)


def test_chat_remembers_earlier_messages_in_same_conversation(db_session, monkeypatch):
    monkeypatch.setattr(
        llm_service_module.llm_service,
        "chat",
        lambda messages: f"echo: {messages[-1]['content']}",
    )

    first = client.post("/chat", json={"message": "My name is Manpreet."})
    conversation_id = first.json()["conversation_id"]

    second = client.post(
        "/chat",
        json={"message": "What is my name?", "conversation_id": conversation_id},
    )
    assert second.status_code == 200

    detail = client.get(f"/conversations/{conversation_id}")
    messages = detail.json()["messages"]
    assert len(messages) == 4
    assert messages[0]["content"] == "My name is Manpreet."
    assert messages[2]["content"] == "What is my name?"


def test_chat_sets_conversation_title_from_first_message(db_session, monkeypatch):
    monkeypatch.setattr(llm_service_module.llm_service, "chat", lambda messages: "a reply")

    response = client.post("/chat", json={"message": "What is supervised learning?"})
    conversation_id = response.json()["conversation_id"]

    detail = client.get(f"/conversations/{conversation_id}")
    assert detail.json()["title"] == "What is supervised learning?"


def test_chat_rejects_empty_message(db_session):
    response = client.post("/chat", json={"message": ""})
    assert response.status_code == 422


def test_chat_returns_404_for_unknown_conversation(db_session):
    response = client.post("/chat", json={"message": "hi", "conversation_id": 9999})
    assert response.status_code == 404


def test_chat_returns_503_when_llm_not_configured(db_session, monkeypatch):
    def raise_not_configured(messages):
        raise llm_service_module.LLMNotConfiguredError("not configured")

    monkeypatch.setattr(llm_service_module.llm_service, "chat", raise_not_configured)

    response = client.post("/chat", json={"message": "hello"})
    assert response.status_code == 503


# A 1x1 transparent PNG, base64-encoded, just for exercising the image path.
TINY_PNG_BASE64 = (
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42"
    "YAAAAASUVORK5CYII="
)


def test_chat_accepts_image_only_message_without_text(db_session, monkeypatch):
    captured = {}

    def fake_chat(messages):
        captured["messages"] = messages
        return "I see a small image."

    monkeypatch.setattr(llm_service_module.llm_service, "chat", fake_chat)

    response = client.post(
        "/chat",
        json={
            "message": "",
            "image_data": TINY_PNG_BASE64,
            "image_media_type": "image/png",
        },
    )

    assert response.status_code == 200
    last_content = captured["messages"][-1]["content"]
    assert isinstance(last_content, list)
    assert last_content[0]["type"] == "image"
    assert last_content[0]["source"]["media_type"] == "image/png"
    assert last_content[1]["type"] == "text"


def test_chat_stores_placeholder_text_for_image_only_message(db_session, monkeypatch):
    monkeypatch.setattr(llm_service_module.llm_service, "chat", lambda messages: "a reply")

    response = client.post(
        "/chat",
        json={"message": "", "image_data": TINY_PNG_BASE64, "image_media_type": "image/png"},
    )
    conversation_id = response.json()["conversation_id"]

    detail = client.get(f"/conversations/{conversation_id}")
    assert detail.json()["messages"][0]["content"] == "[Image attached]"


def test_chat_rejects_unsupported_image_type(db_session):
    response = client.post(
        "/chat",
        json={
            "message": "what is this",
            "image_data": TINY_PNG_BASE64,
            "image_media_type": "application/pdf",
        },
    )
    assert response.status_code == 422


def test_chat_rejects_no_text_and_no_image(db_session):
    response = client.post("/chat", json={"message": "   "})
    assert response.status_code == 422
