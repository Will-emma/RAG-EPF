import uuid

import pytest

from app.core.security import hash_password
from app.db.models import User


async def create_user_and_login(client, db_session) -> dict:
    user = User(
        email=f"history-{uuid.uuid4()}@example.com",
        hashed_password=hash_password("Password123!"),
    )
    db_session.add(user)
    await db_session.commit()

    response = await client.post(
        "/api/auth/login",
        json={"email": user.email, "password": "Password123!"},
    )
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


@pytest.fixture
def fake_rag(monkeypatch):
    # On évite le vrai modèle d'embedding et le vrai appel LLM
    async def fake_search(query, user_id, db, top_k=5):
        return [{"course_name": "Cours IA", "filename": "cours.pdf", "page_number": 3, "content": "..."}]

    async def fake_ask_llm(question, chunks):
        return f"Réponse à : {question}"

    monkeypatch.setattr("app.api.routes.chat.search", fake_search)
    monkeypatch.setattr("app.api.routes.chat.ask_llm", fake_ask_llm)


@pytest.mark.asyncio
async def test_chat_messages_are_saved_and_grouped_by_conversation(client, db_session, fake_rag):
    headers = await create_user_and_login(client, db_session)

    first = await client.post("/api/chat/", json={"message": "Qu'est-ce que le RAG ?"}, headers=headers)
    assert first.status_code == 200
    conversation_id = first.json()["conversation_id"]

    second = await client.post(
        "/api/chat/",
        json={"message": "Et les embeddings ?", "conversation_id": conversation_id},
        headers=headers,
    )
    assert second.json()["conversation_id"] == conversation_id

    conversations = (await client.get("/api/history/", headers=headers)).json()
    assert len(conversations) == 1
    assert conversations[0]["title"] == "Qu'est-ce que le RAG ?"
    assert conversations[0]["last_question"] == "Et les embeddings ?"
    assert conversations[0]["message_count"] == 2

    messages = (await client.get(f"/api/history/{conversation_id}", headers=headers)).json()
    assert [m["question"] for m in messages] == ["Qu'est-ce que le RAG ?", "Et les embeddings ?"]
    assert messages[0]["answer"] == "Réponse à : Qu'est-ce que le RAG ?"
    assert messages[0]["sources"] == [{"course": "Cours IA", "page": 3}]

    deleted = await client.delete(f"/api/history/{conversation_id}", headers=headers)
    assert deleted.status_code == 204
    assert (await client.get("/api/history/", headers=headers)).json() == []


@pytest.mark.asyncio
async def test_history_is_isolated_between_users(client, db_session, fake_rag):
    headers_a = await create_user_and_login(client, db_session)
    headers_b = await create_user_and_login(client, db_session)

    response = await client.post("/api/chat/", json={"message": "Question privée de A"}, headers=headers_a)
    conversation_id = response.json()["conversation_id"]

    assert (await client.get("/api/history/", headers=headers_b)).json() == []
    assert (await client.get(f"/api/history/{conversation_id}", headers=headers_b)).status_code == 404
    assert (await client.delete(f"/api/history/{conversation_id}", headers=headers_b)).status_code == 404

    # La conversation de A est intacte
    assert len((await client.get("/api/history/", headers=headers_a)).json()) == 1


@pytest.mark.asyncio
async def test_history_requires_authentication(client):
    response = await client.get("/api/history/")
    assert response.status_code in (401, 403)
