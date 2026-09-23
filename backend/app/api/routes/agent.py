"""
TICKET: AGENT-2 Génération de QCM et évaluation des réponses (Study Agent)
"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.agent.graph import run_qcm_agent
from app.api.deps import get_current_user
from app.db.database import get_db
from app.db.models import User

router = APIRouter(prefix="/agent", tags=["agent"])


class QcmRequest(BaseModel):
    course_name: str | None = None
    num_questions: int = 5


class QcmQuestion(BaseModel):
    question: str
    options: list[str]
    correctAnswer: int


class QcmResponse(BaseModel):
    questions: list[QcmQuestion]


@router.post("/qcm", response_model=QcmResponse)
async def generate_qcm(
    request: QcmRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = request.course_name or "notions et concepts importants du cours"
    result = await run_qcm_agent(
        query=query,
        user_id=current_user.id,
        db=db,
        num_questions=request.num_questions,
    )

    if result.get("error") and not result.get("questions"):
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Impossible de générer le QCM pour le moment. Avez-vous importé un cours ? Réessayez dans un instant.",
        )

    return QcmResponse(questions=result.get("questions", []))