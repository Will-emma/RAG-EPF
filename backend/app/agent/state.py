"""État partagé du Study Agent (LangGraph)."""
from typing import TypedDict

import uuid


class AgentState(TypedDict, total=False):
    # Entrée
    query: str
    user_id: uuid.UUID

    # Intermédiaire
    course: str | None          # cours identifié (None = tous)
    top_k: int

    # Sortie
    chunks: list[dict]          # résultats de search()
    error: str | None