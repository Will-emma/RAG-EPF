from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.database import get_db
from app.db.models import User
from app.rag.search import search as search_chunks
from app.schemas.search import ChunkResult

router = APIRouter(prefix="/search", tags=["search"])


@router.get("/", response_model=list[ChunkResult])
async def search_endpoint(
    q: str = Query(..., min_length=1, description="Question de l'utilisateur"),
    top_k: int = Query(5, ge=1, le=20),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await search_chunks(query=q, user_id=current_user.id, db=db, top_k=top_k)