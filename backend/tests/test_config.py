import pytest

from app.core.config import Settings


@pytest.mark.parametrize(
    ("database_url", "expected"),
    [
        # Format fourni par Render / la plupart des hébergeurs
        ("postgresql://user:pwd@host:5432/db", "postgresql+asyncpg://user:pwd@host:5432/db"),
        ("postgres://user:pwd@host/db", "postgresql+asyncpg://user:pwd@host/db"),
        # Format déjà correct (local, .env.example) : inchangé
        ("postgresql+asyncpg://user:pwd@db:5432/db", "postgresql+asyncpg://user:pwd@db:5432/db"),
    ],
)
def test_database_url_uses_asyncpg_driver(database_url, expected):
    settings = Settings(DATABASE_URL=database_url, JWT_SECRET_KEY="test")
    assert settings.DATABASE_URL == expected
