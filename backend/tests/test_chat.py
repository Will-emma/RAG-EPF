import uuid

import httpx
import pytest

from app.core.security import hash_password
from app.db.models import User


async def create_user_and_login(client, db_session) -> dict:
    user = User(
        email=f"chat-{uuid.uuid4()}@example.com",
        hashed_password=hash_password("Password123!"),
    )
    db_session.add(user)
    await db_session.commit()

    response = await client.post(
        "/api/auth/login",
        json={"email": user.email, "password": "Password123!"},
    )
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def llm_status_error() -> httpx.HTTPStatusError:
    request = httpx.Request("POST", "https://llm.test/chat/completions")
    return httpx.HTTPStatusError("429", request=request, response=httpx.Response(429, request=request))


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("llm_error", "expected_status", "expected_detail"),
    [
        (httpx.ReadTimeout("timeout"), 504, "trop de temps"),
        (llm_status_error(), 502, "Erreur du service IA (429)"),
        # Connexion coupée par le fournisseur au milieu de la réponse
        (httpx.RemoteProtocolError("peer closed connection"), 502, "n'a pas pu répondre"),
        (httpx.ConnectError("unreachable"), 502, "n'a pas pu répondre"),
        # Réponse 200 sans "choices" (ex : fournisseur surchargé)
        (KeyError("choices"), 502, "n'a pas pu répondre"),
    ],
)
async def test_chat_returns_readable_error_when_llm_fails(
    client, db_session, monkeypatch, llm_error, expected_status, expected_detail
):
    async def fake_search(query, user_id, db, top_k=5):
        return [{"course_name": "Cours IA", "filename": "cours.pdf", "page_number": 1, "content": "..."}]

    async def failing_ask_llm(question, chunks):
        raise llm_error

    monkeypatch.setattr("app.api.routes.chat.search", fake_search)
    monkeypatch.setattr("app.api.routes.chat.ask_llm", failing_ask_llm)
    headers = await create_user_and_login(client, db_session)

    response = await client.post("/api/chat/", json={"message": "Question ?"}, headers=headers)

    assert response.status_code == expected_status
    assert expected_detail in response.json()["detail"]
    # Un échange en échec n'est pas enregistré dans l'historique
    assert (await client.get("/api/history/", headers=headers)).json() == []
