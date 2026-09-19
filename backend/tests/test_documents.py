import io

import pytest
from docx import Document as DocxDocument
from fastapi.testclient import TestClient

from app.api import documents as documents_api
from app.main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def isolate_upload_dir(tmp_path, monkeypatch):
    """Keep tests from writing real files into the project's data/uploads/."""
    monkeypatch.setattr(documents_api, "UPLOAD_DIR", tmp_path)


def _txt_file(content: str, filename: str = "notes.txt"):
    return {"file": (filename, io.BytesIO(content.encode("utf-8")), "text/plain")}


def _docx_file(paragraphs: list[str], filename: str = "resume.docx"):
    doc = DocxDocument()
    for p in paragraphs:
        doc.add_paragraph(p)
    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return {
        "file": (
            filename,
            buffer,
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )
    }


def test_upload_requires_auth(db_session):
    response = client.post("/documents/upload", files=_txt_file("hello"))
    assert response.status_code == 401


def test_upload_txt_document_success(db_session, auth_headers):
    response = client.post(
        "/documents/upload",
        files=_txt_file("This is a simple test document about Python."),
        headers=auth_headers,
    )

    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "ready"
    assert body["filename"] == "notes.txt"
    assert body["chunk_count"] >= 1


def test_upload_docx_document_success(db_session, auth_headers):
    response = client.post(
        "/documents/upload",
        files=_docx_file(["Experience with Python.", "Built REST APIs."]),
        headers=auth_headers,
    )

    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "ready"
    assert body["chunk_count"] >= 1


def test_upload_rejects_unsupported_file_type(db_session, auth_headers):
    files = {"file": ("archive.zip", io.BytesIO(b"PK\x03\x04"), "application/zip")}
    response = client.post("/documents/upload", files=files, headers=auth_headers)

    assert response.status_code == 400


def test_upload_rejects_oversized_file(db_session, auth_headers, monkeypatch):
    from app.services import document_service

    monkeypatch.setattr(document_service, "MAX_FILE_SIZE_BYTES", 10)
    response = client.post(
        "/documents/upload",
        files=_txt_file("this is longer than 10 bytes"),
        headers=auth_headers,
    )

    assert response.status_code == 413


def test_upload_empty_document_marks_status_failed(db_session, auth_headers):
    response = client.post(
        "/documents/upload", files=_txt_file("   "), headers=auth_headers
    )

    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "failed"
    assert body["error_message"]


def test_list_documents(db_session, auth_headers):
    client.post("/documents/upload", files=_txt_file("Doc one content."), headers=auth_headers)
    client.post(
        "/documents/upload",
        files=_txt_file("Doc two content.", filename="two.txt"),
        headers=auth_headers,
    )

    response = client.get("/documents", headers=auth_headers)

    assert response.status_code == 200
    assert len(response.json()) == 2


def test_get_document_detail(db_session, auth_headers):
    upload = client.post(
        "/documents/upload", files=_txt_file("Some content here."), headers=auth_headers
    )
    document_id = upload.json()["id"]

    response = client.get(f"/documents/{document_id}", headers=auth_headers)

    assert response.status_code == 200
    assert response.json()["filename"] == "notes.txt"


def test_get_missing_document_returns_404(db_session, auth_headers):
    response = client.get("/documents/9999", headers=auth_headers)
    assert response.status_code == 404


def test_delete_document(db_session, auth_headers):
    upload = client.post(
        "/documents/upload", files=_txt_file("Delete me."), headers=auth_headers
    )
    document_id = upload.json()["id"]

    delete_response = client.delete(f"/documents/{document_id}", headers=auth_headers)
    assert delete_response.status_code == 204

    get_response = client.get(f"/documents/{document_id}", headers=auth_headers)
    assert get_response.status_code == 404


def test_documents_are_isolated_between_users(db_session, auth_headers):
    client.post(
        "/documents/upload", files=_txt_file("user one's document"), headers=auth_headers
    )

    other = client.post(
        "/auth/register", json={"email": "other-doc@example.com", "password": "password123"}
    )
    other_headers = {"Authorization": f"Bearer {other.json()['access_token']}"}

    response = client.get("/documents", headers=other_headers)
    assert response.status_code == 200
    assert response.json() == []
