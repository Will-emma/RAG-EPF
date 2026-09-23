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
    num_questions: int          # nombre de questions QCM à générer

    # Sortie
    chunks: list[dict]          # résultats de search()
    questions: list[dict]       # résultats du QCM généré
    error: str | None