import logging
import time

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "Tu es un assistant pédagogique pour des étudiants de l'EPF. "
    "Réponds uniquement à partir du contexte fourni, extrait des cours de l'étudiant. "
    "Si le contexte ne permet pas de répondre, dis-le clairement plutôt que d'inventer. "
    "Réponds en français, de façon claire et concise."
)


def build_context(chunks: list[dict]) -> str:
    parts = []
    for c in chunks:
        course = c.get("course_name") or c.get("filename")
        page = c.get("page_number")
        parts.append(f"[Source: {course}, page {page}]\n{c['content']}")
    return "\n\n---\n\n".join(parts)


async def call_llm(system_prompt: str, user_prompt: str, temperature: float = 0.3) -> str:
    """Appel générique au LLM (OpenRouter), réutilisable par le chat et par le Study Agent."""
    started_at = time.perf_counter()
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{settings.LLM_BASE_URL}/chat/completions",
                headers={"Authorization": f"Bearer {settings.LLM_API_KEY}"},
                json={
                    "model": settings.LLM_MODEL,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    "temperature": temperature,
                },
            )
        response.raise_for_status()
    except httpx.HTTPError as exc:
        logger.warning(
            "LLM request failed (model=%s, error_type=%s, duration_ms=%d)",
            settings.LLM_MODEL,
            type(exc).__name__,
            round((time.perf_counter() - started_at) * 1000),
        )
        raise

    duration_ms = round((time.perf_counter() - started_at) * 1000)
    try:
        data = response.json()
        result = data["choices"][0]["message"]["content"]
    except (ValueError, KeyError, IndexError, TypeError):
        logger.warning(
            "LLM response parsing failed (model=%s, status_code=%d, duration_ms=%d)",
            settings.LLM_MODEL,
            response.status_code,
            duration_ms,
        )
        raise

    logger.info(
        "LLM request completed (model=%s, status_code=%d, duration_ms=%d)",
        settings.LLM_MODEL,
        response.status_code,
        duration_ms,
    )
    return result


async def ask_llm(question: str, chunks: list[dict]) -> str:
    context = build_context(chunks)
    user_prompt = (
        f"Contexte extrait des cours :\n\n{context}\n\n"
        f"Question de l'étudiant : {question}"
    )
    return await call_llm(SYSTEM_PROMPT, user_prompt)
