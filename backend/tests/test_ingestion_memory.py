import uuid

import pytest
from sqlalchemy import select

from app.core.security import hash_password
from app.db.database import mark_interrupted_documents
from app.db.models import Document, User
from app.rag import ingestion


def test_embed_texts_uses_small_batches(monkeypatch):
    # Paquets de 256 (défaut fastembed) : dépassement des 512 Mo de Render
    calls = []

    class FakeVector(list):
        def tolist(self):
            return list(self)

    class FakeModel:
        def embed(self, texts, batch_size):
            calls.append(batch_size)
            return [FakeVector([0.0] * 384) for _ in texts]

    monkeypatch.setattr(ingestion, "get_embedding_model", lambda: FakeModel())

    vectors = ingestion.embed_texts(["passage"] * 20)

    assert len(vectors) == 20
    assert calls == [ingestion.EMBEDDING_BATCH_SIZE]
    assert ingestion.EMBEDDING_BATCH_SIZE <= 16


@pytest.mark.asyncio
async def test_interrupted_documents_are_marked_as_error(db_session):
    user = User(email=f"stuck-{uuid.uuid4()}@example.com", hashed_password=hash_password("Password123!"))
    db_session.add(user)
    await db_session.commit()

    statuses = ["ready", "processing", "uploaded", "error"]
    db_session.add_all(
        [Document(owner_id=user.id, filename=f"{status}.pdf", status=status) for status in statuses]
    )
    await db_session.commit()

    await mark_interrupted_documents(db_session)
    await db_session.commit()

    result = await db_session.execute(select(Document.filename, Document.status).where(Document.owner_id == user.id))
    after = dict(result.all())
    assert after == {
        "ready.pdf": "ready",          # déjà traité : inchangé
        "processing.pdf": "error",     # interrompu en plein traitement
        "uploaded.pdf": "error",       # interrompu avant le traitement
        "error.pdf": "error",
    }
