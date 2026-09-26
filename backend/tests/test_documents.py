import io
import uuid
import zipfile
from unittest.mock import patch

import pytest

from app.core.security import hash_password
from app.db.models import Document, User


async def _registered_user_headers(client, prefix="upload"):
    email = f"{prefix}-{uuid.uuid4()}@example.com"
    password = "TestPassword123!"
    registration = await client.post(
        "/api/auth/register", json={"email": email, "password": password}
    )
    assert registration.status_code == 201

    login = await client.post(
        "/api/auth/login", json={"email": email, "password": password}
    )
    assert login.status_code == 200
    return {"Authorization": f"Bearer {login.json()['access_token']}"}


def _office_package(part_name: str, main_content_type: str) -> bytes:
    contents = io.BytesIO()
    content_types = (
        f'<Types><Override PartName="/{part_name}" '
        f'ContentType="{main_content_type}"/></Types>'
    )
    with zipfile.ZipFile(contents, "w") as archive:
        archive.writestr("[Content_Types].xml", content_types)
        archive.writestr(part_name, "<document/>")
    return contents.getvalue()


@pytest.mark.asyncio
async def test_upload_rejects_invalid_extension(client):
    headers = await _registered_user_headers(client)
    response = await client.post(
        "/api/documents/upload",
        headers=headers,
        files={"file": ("cours.txt", io.BytesIO(b"contenu de test"), "text/plain")},
    )
    assert response.status_code == 400
    assert "Extension non autorisée" in response.json()["detail"]


@pytest.mark.asyncio
async def test_upload_rejects_allowed_extension_with_wrong_content(client):
    headers = await _registered_user_headers(client)
    response = await client.post(
        "/api/documents/upload",
        headers=headers,
        files={"file": ("cours.pdf", io.BytesIO(b"not a PDF"), "application/pdf")},
    )
    assert response.status_code == 400
    assert "ne correspond pas" in response.json()["detail"]


@pytest.mark.asyncio
async def test_upload_valid_pdf(client):
    headers = await _registered_user_headers(client, "upload-pdf")
    with (
        patch(
            "app.api.routes.documents.extract_pages",
            return_value=[(1, "Contenu de test")],
        ),
        patch("app.api.routes.documents.embed_texts", return_value=[[0.0] * 384]),
    ):
        response = await client.post(
            "/api/documents/upload",
            headers=headers,
            files={
                "file": (
                    "cours.pdf",
                    io.BytesIO(b"%PDF-1.4\ncontenu PDF simule"),
                    "application/octet-stream",
                )
            },
        )

    assert response.status_code == 201
    assert response.json()["filename"] == "cours.pdf"
    assert response.json()["status"] == "ready"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("filename", "part_name", "main_content_type"),
    [
        (
            "cours.docx",
            "word/document.xml",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml",
        ),
        (
            "cours.pptx",
            "ppt/presentation.xml",
            "application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml",
        ),
    ],
)
async def test_upload_accepts_supported_office_formats(
    client, filename, part_name, main_content_type
):
    headers = await _registered_user_headers(client, "upload-office")
    package = _office_package(part_name, main_content_type)
    with (
        patch(
            "app.api.routes.documents.extract_pages",
            return_value=[(1, "Contenu de test")],
        ),
        patch("app.api.routes.documents.embed_texts", return_value=[[0.0] * 384]),
    ):
        response = await client.post(
            "/api/documents/upload",
            headers=headers,
            files={"file": (filename, io.BytesIO(package), "application/octet-stream")},
        )

    assert response.status_code == 201
    assert response.json()["filename"] == filename


@pytest.mark.asyncio
async def test_upload_rejects_file_over_size_limit(client, monkeypatch):
    monkeypatch.setattr("app.api.routes.documents.settings.MAX_UPLOAD_SIZE_MB", 1)
    headers = await _registered_user_headers(client, "upload-large")
    contents = b"%PDF-1.4\n" + b"x" * (1024 * 1024)
    response = await client.post(
        "/api/documents/upload",
        headers=headers,
        files={"file": ("cours.pdf", io.BytesIO(contents), "application/pdf")},
    )
    assert response.status_code == 400
    assert "trop volumineux" in response.json()["detail"]


@pytest.mark.asyncio
async def test_document_list_only_returns_current_users_documents(
    client, db_session
):
    password = "Password123!"
    user_a = User(
        email=f"owner-a-{uuid.uuid4()}@example.com",
        hashed_password=hash_password(password),
    )
    user_b = User(
        email=f"owner-b-{uuid.uuid4()}@example.com",
        hashed_password=hash_password(password),
    )
    db_session.add_all([user_a, user_b])
    await db_session.flush()
    db_session.add_all(
        [
            Document(owner_id=user_a.id, filename="user-a.pdf", status="ready"),
            Document(owner_id=user_b.id, filename="user-b.pdf", status="ready"),
        ]
    )
    await db_session.commit()

    login = await client.post(
        "/api/auth/login", json={"email": user_b.email, "password": password}
    )
    assert login.status_code == 200
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    response = await client.get("/api/documents/", headers=headers)

    assert response.status_code == 200
    assert [document["filename"] for document in response.json()] == ["user-b.pdf"]


@pytest.mark.asyncio
async def test_upload_processing_error_is_logged_without_exception_text(
    client, caplog
):
    headers = await _registered_user_headers(client, "upload-error")
    with patch(
        "app.api.routes.documents.extract_pages",
        side_effect=RuntimeError("sensitive document text"),
    ):
        response = await client.post(
            "/api/documents/upload",
            headers=headers,
            files={
                "file": (
                    "cours.pdf",
                    io.BytesIO(b"%PDF-1.4\ncontenu"),
                    "application/pdf",
                )
            },
        )

    assert response.status_code == 201
    assert response.json()["status"] == "error"
    assert "Document processing failed" in caplog.text
    assert "RuntimeError" in caplog.text
    assert "sensitive document text" not in caplog.text

async def register_and_login(client) -> dict:
    email = f"delete-{uuid.uuid4()}@example.com"
    password = "TestPassword123!"
    await client.post("/api/auth/register", json={"email": email, "password": password})
    login_response = await client.post("/api/auth/login", json={"email": email, "password": password})
    return {"Authorization": f"Bearer {login_response.json()['access_token']}"}


async def upload_fake_pdf(client, headers) -> str:
    with patch("app.api.routes.documents.extract_pages", return_value=[(1, "Contenu de test")]), \
         patch("app.api.routes.documents.embed_texts", return_value=[[0.0] * 384]):
        response = await client.post(
            "/api/documents/upload",
            headers=headers,
            files={"file": ("cours.pdf", io.BytesIO(b"%PDF-1.4\ncontenu PDF simule"), "application/pdf")},
        )
    assert response.status_code == 201
    return response.json()["id"]


@pytest.mark.asyncio
async def test_delete_document_removes_document_chunks_and_file(client, db_session):
    from pathlib import Path
    from sqlalchemy import func, select
    from app.db.models import Chunk

    headers = await register_and_login(client)
    document_id = await upload_fake_pdf(client, headers)
    assert Path(f"uploads/{document_id}.pdf").exists()

    response = await client.delete(f"/api/documents/{document_id}", headers=headers)
    assert response.status_code == 204

    assert (await client.get("/api/documents/", headers=headers)).json() == []
    chunk_count = await db_session.scalar(
        select(func.count()).select_from(Chunk).where(Chunk.document_id == uuid.UUID(document_id))
    )
    assert chunk_count == 0
    assert not Path(f"uploads/{document_id}.pdf").exists()


@pytest.mark.asyncio
async def test_delete_document_of_another_user_returns_404(client):
    headers_a = await register_and_login(client)
    headers_b = await register_and_login(client)
    document_id = await upload_fake_pdf(client, headers_a)

    response = await client.delete(f"/api/documents/{document_id}", headers=headers_b)
    assert response.status_code == 404

    # Le document de A est toujours là
    assert len((await client.get("/api/documents/", headers=headers_a)).json()) == 1

    # Nettoyage du fichier stocké
    assert (await client.delete(f"/api/documents/{document_id}", headers=headers_a)).status_code == 204


@pytest.mark.asyncio
async def test_delete_document_requires_authentication(client):
    response = await client.delete(f"/api/documents/{uuid.uuid4()}")
    assert response.status_code in (401, 403)
