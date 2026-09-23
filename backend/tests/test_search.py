import uuid

import pytest
from sqlalchemy import select

from app.core.security import hash_password
from app.db.models import Chunk, Document, User


@pytest.mark.asyncio
async def test_search_isolates_users(client, db_session):
    # Création de deux utilisateurs
    user_a = User(
        email=f"user-a-{uuid.uuid4()}@example.com",
        hashed_password=hash_password("Password123!"),
    )
    user_b = User(
        email=f"user-b-{uuid.uuid4()}@example.com",
        hashed_password=hash_password("Password123!"),
    )

    db_session.add_all([user_a, user_b])
    await db_session.commit()
    await db_session.refresh(user_a)
    await db_session.refresh(user_b)

    # Document appartenant à l'utilisateur A
    document_a = Document(
        owner_id=user_a.id,
        filename="cours-user-a.pdf",
        status="ready",
    )

    db_session.add(document_a)
    await db_session.commit()
    await db_session.refresh(document_a)

    # Contenu du document de A
    chunk_a = Chunk(
        document_id=document_a.id,
        content="Cours secret de l'utilisateur A",
        page_number=1,
        embedding=[0.0] * 384,
    )

    db_session.add(chunk_a)
    await db_session.commit()

    # Connexion de l'utilisateur B
    login_response = await client.post(
        "/api/auth/login",
        json={
            "email": user_b.email,
            "password": "Password123!",
        },
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    # On évite de charger le vrai modèle d'embedding
    with pytest.MonkeyPatch.context() as monkeypatch:
        monkeypatch.setattr(
            "app.rag.search.embed_texts",
            lambda texts: [[0.0] * 384],
        )

        response = await client.get(
            "/api/search/",
            params={"q": "cours"},
            headers={"Authorization": f"Bearer {token}"},
        )

    assert response.status_code == 200
    assert response.json() == []