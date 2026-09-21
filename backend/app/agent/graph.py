"""Study Agent — squelette LangGraph (AGENT-1).

Graphe minimal :
    [START] → identify → query_rag → [END]

- identify   : identifie le cours/chapitre visé (version simple : laisse passer)
- query_rag  : appelle app.rag.search.search() pour récupérer les chunks
"""
import uuid

from langgraph.graph import StateGraph, END
from sqlalchemy.ext.asyncio import AsyncSession

from app.agent.state import AgentState
from app.rag.search import search


async def identify_node(state: AgentState, db: AsyncSession) -> AgentState:
    """Identifie le cours/chapitre à interroger.

    Version simple (Sprint 2) : on ne filtre pas encore par cours,
    on transmet la requête telle quelle. À enrichir plus tard (AGENT-2).
    """
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


# --- gestion simple de la db via contexte -------------------------------

_DB_CTX: dict[str, AsyncSession] = {}


def _get_db() -> AsyncSession:
    if "db" not in _DB_CTX:
        raise RuntimeError("DB non initialisée : utilisez run_agent(db=...)")
    return _DB_CTX["db"]


def build_graph():
    """Construit le graphe LangGraph."""
    graph = StateGraph(AgentState)

    async def _identify(state: AgentState) -> AgentState:
        return await identify_node(state, db=_get_db())

    async def _query_rag(state: AgentState) -> AgentState:
        return await query_rag_node(state, db=_get_db())

    graph.add_node("identify", _identify)
    graph.add_node("query_rag", _query_rag)
    graph.set_entry_point("identify")
    graph.add_edge("identify", "query_rag")
    graph.add_edge("query_rag", END)

    return graph.compile()


async def run_agent(
    query: str,
    user_id: uuid.UUID,
    db: AsyncSession,
    top_k: int = 5,
) -> AgentState:
    """Point d'entrée pratique pour exécuter l'agent."""
    _DB_CTX["db"] = db
    try:
        agent = build_graph()
        initial: AgentState = {"query": query, "user_id": user_id, "top_k": top_k}
        return await agent.ainvoke(initial)
    finally:
        _DB_CTX.pop("db", None)