import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Chunk, Document
from app.rag.ingestion import embed_texts


async def search(query: str, user_id: uuid.UUID, db: AsyncSession, top_k: int = 5):
    """Retourne les top_k chunks les plus pertinents pour une question,
    limités aux documents de l'utilisateur donné."""
    query_embedding = embed_texts([query])[0]

    distance = Chunk.embedding.cosine_distance(query_embedding)
    stmt = (
        select(Chunk, Document, distance.label("distance"))
        .join(Document, Chunk.document_id == Document.id)
        .where(Document.owner_id == user_id)
        .order_by(distance)
        .limit(top_k)
    )
    result = await db.execute(stmt)
    rows = result.all()

    results = []
    for chunk, document, dist in rows:
        results.append(
            {
                "chunk_id": chunk.id,
                "document_id": document.id,
                "filename": document.filename,
                "course_name": document.course_name,
                "page_number": chunk.page_number,
                "content": chunk.content,
                "score": 1 - dist,  # similarité cosinus = 1 - distance cosinus
            }
        )
    return results