import pytest
from fastapi.testclient import TestClient

from app.api import images as images_api
from app.main import app
from app.services import image_service as image_service_module

client = TestClient(app)

FAKE_RESULT_BYTES = b"fake-generated-png-bytes"


@pytest.fixture(autouse=True)
def isolate_generated_dir(tmp_path, monkeypatch):
    """Keep tests from writing real files into the project's data/generated/."""
    monkeypatch.setattr(images_api, "GENERATED_DIR", tmp_path)


@pytest.fixture(autouse=True)
def stub_image_service(monkeypatch):
    monkeypatch.setattr(
        image_service_module.image_service,
        "generate_image",
        lambda prompt: (FAKE_RESULT_BYTES, "image/png"),
    )


def test_generate_image_requires_auth(db_session):
    response = client.post("/images/generate", json={"prompt": "a 3D pixar robot"})
    assert response.status_code == 401


def test_generate_image_creates_conversation_and_message(db_session, auth_headers):
    import base64

    response = client.post(
        "/images/generate", json={"prompt": "a 3D pixar robot"}, headers=auth_headers
    )

    assert response.status_code == 201
    body = response.json()
    assert body["image_id"]
    assert base64.b64decode(body["image_data"]) == FAKE_RESULT_BYTES
    conversation_id = body["conversation_id"]

    detail = client.get(f"/conversations/{conversation_id}", headers=auth_headers)
    messages = detail.json()["messages"]
    assert len(messages) == 2
    assert messages[0]["content"] == "a 3D pixar robot"
    assert messages[1]["generated_image_id"] == body["image_id"]
    assert detail.json()["title"] == "a 3D pixar robot"


def test_generate_image_reuses_existing_conversation(db_session, auth_headers):
    first = client.post(
        "/images/generate", json={"prompt": "first image"}, headers=auth_headers
    )
    conversation_id = first.json()["conversation_id"]

    second = client.post(
        "/images/generate",
        json={"prompt": "second image", "conversation_id": conversation_id},
        headers=auth_headers,
    )
    assert second.status_code == 201
    assert second.json()["conversation_id"] == conversation_id

    detail = client.get(f"/conversations/{conversation_id}", headers=auth_headers)
    assert len(detail.json()["messages"]) == 4


def test_generate_image_rejects_empty_prompt(db_session, auth_headers):
    response = client.post("/images/generate", json={"prompt": ""}, headers=auth_headers)
    assert response.status_code == 422


def test_generate_image_returns_502_on_service_error(db_session, auth_headers, monkeypatch):
    def raise_error(prompt):
        raise image_service_module.ImageServiceError("upstream failed")

    monkeypatch.setattr(image_service_module.image_service, "generate_image", raise_error)

    response = client.post(
        "/images/generate", json={"prompt": "test"}, headers=auth_headers
    )
    assert response.status_code == 502


def test_generate_image_returns_502_when_no_image_returned(db_session, auth_headers, monkeypatch):
    def raise_no_image(prompt):
        raise image_service_module.NoImageReturnedError("no image")

    monkeypatch.setattr(image_service_module.image_service, "generate_image", raise_no_image)

    response = client.post(
        "/images/generate", json={"prompt": "test"}, headers=auth_headers
    )
    assert response.status_code == 502


def test_get_generated_image_returns_bytes(db_session, auth_headers):
    gen_response = client.post(
        "/images/generate", json={"prompt": "test"}, headers=auth_headers
    )
    image_id = gen_response.json()["image_id"]

    response = client.get(f"/images/{image_id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"
    assert response.content == FAKE_RESULT_BYTES


def test_get_generated_image_requires_auth(db_session, auth_headers):
    gen_response = client.post(
        "/images/generate", json={"prompt": "test"}, headers=auth_headers
    )
    image_id = gen_response.json()["image_id"]

    response = client.get(f"/images/{image_id}")
    assert response.status_code == 401


def test_generated_images_are_isolated_between_users(db_session, auth_headers):
    gen_response = client.post(
        "/images/generate", json={"prompt": "user one's image"}, headers=auth_headers
    )
    image_id = gen_response.json()["image_id"]

    other = client.post(
        "/auth/register", json={"email": "other-image@example.com", "password": "password123"}
    )
    other_headers = {"Authorization": f"Bearer {other.json()['access_token']}"}

    response = client.get(f"/images/{image_id}", headers=other_headers)
    assert response.status_code == 404
