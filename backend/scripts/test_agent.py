"""Script de test local pour AGENT-1.

Usage (depuis backend/) :
    python -m scripts.test_agent
"""
import asyncio

from sqlalchemy import select
from app.db.database import AsyncSessionLocal, init_models
from app.agent.graph import run_agent
from app.db.database import AsyncSessionLocal
from app.db.models import User, Document


async def main():

    await init_models()
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(User)
            .join(Document, Document.owner_id == User.id)
            .where(Document.status == "ready")
            .limit(1)
        )
        user = result.scalar_one_or_none()
        if user is None:
            print("Aucun utilisateur en base — créez-en un d'abord.")
            return

        docs = await db.execute(
            select(Document).where(Document.owner_id == user.id, Document.status == "ready")
        )
        ready_docs = docs.scalars().all()
        print(f"Utilisateur: {user.email} — {len(ready_docs)} document(s) prêt(s)")

        query = "De quoi parle le cours ?"
        print(f"\nQuestion: {query}\n")

        final_state = await run_agent(
            query=query,
            user_id=user.id,
            db=db,
            top_k=3,
        )

        if final_state.get("error"):
            print(f"Erreur: {final_state['error']}")
            return

        chunks = final_state.get("chunks", [])
        print(f"{len(chunks)} chunk(s) trouvé(s):\n")
        for i, c in enumerate(chunks, 1):
            print(f"[{i}] {c['course_name']} — page {c['page_number']} (score={c['score']:.3f})")
            print(f"    {c['content'][:120]}...\n")


if __name__ == "__main__":
    asyncio.run(main())