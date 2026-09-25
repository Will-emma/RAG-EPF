"""
TICKET: FRONT-5 Historique des échanges
Toutes les requêtes filtrent par utilisateur courant (SEC-1).
"""
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Response, status
from pydantic import BaseModel
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.database import get_db
from app.db.models import ChatMessage, User

router = APIRouter(prefix="/history", tags=["history"])


class ConversationSummary(BaseModel):
    conversation_id: uuid.UUID
    title: str              # première question de la conversation
    last_question: str
    message_count: int
    updated_at: datetime


class HistorySource(BaseModel):
    course: str | None
    page: int | None


class HistoryMessage(BaseModel):
    id: uuid.UUID
    question: str
    answer: str
    sources: list[HistorySource]
    created_at: datetime


@router.get("/", response_model=list[ConversationSummary])
async def list_conversations(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.owner_id == current_user.id)
        .order_by(ChatMessage.created_at)
    )

    conversations: dict[uuid.UUID, ConversationSummary] = {}
    for message in result.scalars():
        summary = conversations.get(message.conversation_id)
        if summary is None:
            conversations[message.conversation_id] = ConversationSummary(
                conversation_id=message.conversation_id,
                title=message.question,
                last_question=message.question,
                message_count=1,
                updated_at=message.created_at,
            )
        else:
            summary.last_question = message.question
            summary.message_count += 1
            summary.updated_at = message.created_at

    return sorted(conversations.values(), key=lambda c: c.updated_at, reverse=True)


@router.get("/{conversation_id}", response_model=list[HistoryMessage])
async def get_conversation(
    conversation_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(ChatMessage)
        .where(
            ChatMessage.owner_id == current_user.id,
            ChatMessage.conversation_id == conversation_id,
        )
        .order_by(ChatMessage.created_at)
    )
    messages = result.scalars().all()
    if not messages:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation introuvable.")
    return messages


@router.delete("/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversation(
    conversation_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        delete(ChatMessage).where(
            ChatMessage.owner_id == current_user.id,
            ChatMessage.conversation_id == conversation_id,
        )
    )
    await db.commit()
    if result.rowcount == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation introuvable.")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
