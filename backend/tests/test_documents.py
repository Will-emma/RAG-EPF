
import io
import uuid

import pytest

from unittest.mock import patch

@pytest.mark.asyncio
async def test_upload_rejects_invalid_extension(client):
    email = f"upload-{uuid.uuid4()}@example.com"
    password = "TestPassword123!"

    # Création de l'utilisateur
    register_response = await client.post(
        "/api/auth/register",
        json={
            "email": email,
            "password": password,
        },
    )
    assert register_response.status_code == 201

    # Connexion pour récupérer le token
    login_response = await client.post(
        "/api/auth/login",
        json={
            "email": email,
            "password": password,
        },
    )
    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    # Tentative d'upload d'un fichier avec une extension interdite
    response = await client.post(
        "/api/documents/upload",
        headers={
            "Authorization": f"Bearer {token}",
        },
        files={
            "file": (
                "cours.txt",
                io.BytesIO(b"contenu de test"),
                "text/plain",
            )
        },
    )

    assert response.status_code == 400
    assert "Extension non autorisée" in response.json()["detail"]

@pytest.mark.asyncio
async def test_upload_valid_pdf(client):
    email = f"upload-pdf-{uuid.uuid4()}@example.com"
    password = "TestPassword123!"

    # Création de l'utilisateur
    register_response = await client.post(
        "/api/auth/register",
        json={
            "email": email,
            "password": password,
        },
    )
    assert register_response.status_code == 201

    # Connexion
    login_response = await client.post(
        "/api/auth/login",
        json={
            "email": email,
            "password": password,
        },
    )
    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    # On simule l'extraction et la création des embeddings
    with patch("app.api.routes.documents.extract_pages", return_value=[(1, "Contenu de test")]), \
         patch("app.api.routes.documents.embed_texts", return_value=[[0.0] * 384]):

        response = await client.post(
            "/api/documents/upload",
            headers={
                "Authorization": f"Bearer {token}",
            },
            files={
                "file": (
                    "cours.pdf",
                    io.BytesIO(b"fake pdf content"),
                    "application/pdf",
                )
            },
        )

    assert response.status_code == 201
    data = response.json()
    assert data["filename"] == "cours.pdf"
    assert data["status"] == "ready"

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
            files={"file": ("cours.pdf", io.BytesIO(b"fake pdf content"), "application/pdf")},
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
