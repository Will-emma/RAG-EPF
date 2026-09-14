"""
TICKET: BACK-3 Service RAG (recherche vectorielle + appel LLM)
TICKET: AGENT-2 Endpoint mode révision / QCM (délègue au Study Agent LangGraph)
"""
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/chat", tags=["chat"])


class ChatRequest(BaseModel):
    message: str
    course_id: str | None = None


class ChatResponse(BaseModel):
    answer: str
    sources: list[dict]


@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest):
    # TODO:
    # 1. Embedder la question (même modèle que l'ingestion)
    # 2. Recherche top-K par similarité cosinus dans `chunks` (pgvector)
    # 3. Construire le contexte (chunks + métadonnées page/cours)
    # 4. Appeler le LLM Z.AI (GLM-5.3-Flash) avec le contexte
    # 5. Retourner la réponse + les sources (cours, page)
    raise NotImplementedError
