
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