"""
TICKET: RAG-2 Génération de réponse avec sources
TICKET: FRONT-5 Historique — chaque échange est enregistré dans chat_messages
"""
import uuid

import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.database import get_db
from app.db.models import ChatMessage, User
from app.rag.llm import ask_llm
from app.rag.search import search

router = APIRouter(prefix="/chat", tags=["chat"])


class ChatRequest(BaseModel):
    message: str
    course_id: str | None = None
    # Absent pour le premier message : une nouvelle conversation est créée.
    conversation_id: uuid.UUID | None = None


class Source(BaseModel):
    course: str | None
    page: int | None


class ChatResponse(BaseModel):
    answer: str
    sources: list[Source]
    conversation_id: uuid.UUID


@router.post("/", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    chunks = await search(query=request.message, user_id=current_user.id, db=db, top_k=5)

    if not chunks:
        answer = "Je n'ai trouvé aucun contenu dans vos cours pour répondre à cette question. Avez-vous importé le cours correspondant ?"
        sources = []
    else:
        try:
            answer = await ask_llm(request.message, chunks)
        except httpx.TimeoutException:
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail="Le service IA met trop de temps à répondre. Réessayez dans un instant.",
            )
        except httpx.HTTPStatusError as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Erreur du service IA ({exc.response.status_code}). Réessayez plus tard.",
            )

        seen = set()
        sources = []
        for c in chunks:
            course = c.get("course_name") or c.get("filename")
            page = c.get("page_number")
            key = (course, page)
            if key not in seen:
                seen.add(key)
                sources.append({"course": course, "page": page})

    conversation_id = request.conversation_id or uuid.uuid4()
    db.add(
        ChatMessage(
            owner_id=current_user.id,
            conversation_id=conversation_id,
            question=request.message,
            answer=answer,
            sources=sources,
        )
    )
    await db.commit()

    return ChatResponse(answer=answer, sources=sources, conversation_id=conversation_id)
