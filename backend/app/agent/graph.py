"""Study Agent — LangGraph (AGENT-1 + AGENT-2).

Deux graphes :
    - chat : [START] → identify → query_rag → [END]  (utilisé par RAG-2/chat)
    - qcm  : [START] → identify → query_rag → generate_questions → [END]
"""
import json
import uuid

from langgraph.graph import StateGraph, END
from sqlalchemy.ext.asyncio import AsyncSession

from app.agent.state import AgentState
from app.rag.llm import call_llm
from app.rag.search import search

QCM_SYSTEM_PROMPT = (
    "Tu es un générateur de quiz pédagogique pour des étudiants de l'EPF. "
    "À partir d'extraits de cours, tu génères des questions à choix multiples (QCM) "
    "en français, pertinentes et vérifiables directement dans le contexte fourni. "
    "Réponds UNIQUEMENT avec un tableau JSON valide, sans aucun texte autour, au format exact :\n"
    '[{"question": "...", "options": ["...", "...", "...", "..."], "correctAnswer": 0}]\n'
    "- \"options\" contient exactement 4 propositions plausibles.\n"
    "- \"correctAnswer\" est l'index (0 à 3) de la bonne réponse dans \"options\".\n"
    "- Ne pose des questions que sur des éléments explicitement présents dans le contexte."
)


async def identify_node(state: AgentState, db: AsyncSession) -> AgentState:
    """Identifie le cours/chapitre à interroger (version simple : laisse passer)."""
    state.setdefault("course", None)
    state.setdefault("top_k", 5)
    return state


async def query_rag_node(state: AgentState, db: AsyncSession) -> AgentState:
    """Interroge le service RAG (RAG-1) avec la requête courante."""
    try:
        chunks = await search(
            query=state["query"],
            user_id=state["user_id"],
            db=db,
            top_k=state.get("top_k", 5),
        )
        state["chunks"] = chunks
        state["error"] = None
    except Exception as e:  # noqa: BLE001
        state["chunks"] = []
        state["error"] = str(e)
    return state


async def generate_questions_node(state: AgentState) -> AgentState:
    """Génère un QCM à partir des chunks trouvés par query_rag_node."""
    chunks = state.get("chunks") or []
    if not chunks:
        state["questions"] = []
        state["error"] = state.get("error") or "Aucun contenu de cours trouvé pour générer des questions."
        return state

    context = "\n\n---\n\n".join(c["content"] for c in chunks)
    num_questions = state.get("num_questions", 5)
    user_prompt = (
        f"Génère exactement {num_questions} questions à choix multiples à partir de ce contexte "
        f"extrait des cours de l'étudiant :\n\n{context}"
    )

    try:
        raw = await call_llm(QCM_SYSTEM_PROMPT, user_prompt, temperature=0.5)
        questions = json.loads(raw)
        assert isinstance(questions, list)
        for q in questions:
            assert "question" in q and "options" in q and "correctAnswer" in q
        state["questions"] = questions
        state["error"] = None
    except Exception as e:  # noqa: BLE001
        state["questions"] = []
        state["error"] = f"Erreur de génération du QCM : {e}"
    return state


def build_graph(db: AsyncSession):
    """Graphe chat : identify → query_rag."""
    graph = StateGraph(AgentState)

    async def _identify(state: AgentState) -> AgentState:
        return await identify_node(state, db=db)

    async def _query_rag(state: AgentState) -> AgentState:
        return await query_rag_node(state, db=db)

    graph.add_node("identify", _identify)
    graph.add_node("query_rag", _query_rag)
    graph.set_entry_point("identify")
    graph.add_edge("identify", "query_rag")
    graph.add_edge("query_rag", END)

    return graph.compile()


def build_qcm_graph(db: AsyncSession):
    """Graphe QCM : identify → query_rag → generate_questions."""
    graph = StateGraph(AgentState)

    async def _identify(state: AgentState) -> AgentState:
        return await identify_node(state, db=db)

    async def _query_rag(state: AgentState) -> AgentState:
        return await query_rag_node(state, db=db)

    async def _generate(state: AgentState) -> AgentState:
        return await generate_questions_node(state)

    graph.add_node("identify", _identify)
    graph.add_node("query_rag", _query_rag)
    graph.add_node("generate_questions", _generate)
    graph.set_entry_point("identify")
    graph.add_edge("identify", "query_rag")
    graph.add_edge("query_rag", "generate_questions")
    graph.add_edge("generate_questions", END)

    return graph.compile()


async def run_agent(
    query: str,
    user_id: uuid.UUID,
    db: AsyncSession,
    top_k: int = 5,
) -> AgentState:
    """Point d'entrée pratique pour le graphe chat."""
    agent = build_graph(db)
    initial: AgentState = {"query": query, "user_id": user_id, "top_k": top_k}
    return await agent.ainvoke(initial)


async def run_qcm_agent(
    query: str,
    user_id: uuid.UUID,
    db: AsyncSession,
    num_questions: int = 5,
    top_k: int = 8,
) -> AgentState:
    """Point d'entrée pratique pour le graphe QCM."""
    agent = build_qcm_graph(db)
    initial: AgentState = {
        "query": query,
        "user_id": user_id,
        "top_k": top_k,
        "num_questions": num_questions,
    }
    return await agent.ainvoke(initial)