from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings

engine = create_async_engine(settings.DATABASE_URL, echo=(settings.ENV == "dev"))
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


class Base(DeclarativeBase):
    pass


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

async def mark_interrupted_documents(conn) -> None:
    """Au démarrage, aucun import n'est en cours : un document encore "uploaded"
    ou "processing" a été interrompu (ex : redémarrage du serveur en plein
    traitement). On le passe en "error" pour qu'il ne reste pas bloqué et que
    l'utilisateur puisse le supprimer puis le réimporter."""
    await conn.execute(
        text("UPDATE documents SET status = 'error' WHERE status IN ('uploaded', 'processing')")
    )


async def init_models():
    async with engine.begin() as conn:
        # En local, backend/db/init.sql le fait déjà ; sur une base hébergée
        # (Render), l'extension doit exister avant de créer la table chunks.
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        await conn.run_sync(Base.metadata.create_all)
        await mark_interrupted_documents(conn)
