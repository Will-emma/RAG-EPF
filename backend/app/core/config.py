from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    ENV: str = "dev"

    DATABASE_URL: str

    @field_validator("DATABASE_URL")
    @classmethod
    def use_asyncpg_driver(cls, value: str) -> str:
        # Les hébergeurs (Render...) fournissent "postgresql://" ou "postgres://" ;
        # SQLAlchemy async a besoin du driver explicite "postgresql+asyncpg://".
        for prefix in ("postgresql://", "postgres://"):
            if value.startswith(prefix):
                return "postgresql+asyncpg://" + value[len(prefix):]
        return value

    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    LLM_API_KEY: str = ""
    LLM_BASE_URL: str = "https://openrouter.ai/api/v1"
    LLM_MODEL: str = "z-ai/glm-5.2:free"

    EMBEDDING_PROVIDER: str = "local"
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    # Dossier du modèle d'embedding téléchargé (pré-rempli dans l'image Docker).
    # None = dossier temporaire par défaut de fastembed.
    EMBEDDING_CACHE_DIR: str | None = None
    MISTRAL_API_KEY: str = ""

    MAX_UPLOAD_SIZE_MB: int = 25
    ALLOWED_UPLOAD_EXTENSIONS: str = ".pdf,.pptx,.docx"
    CORS_ORIGINS: str = "http://localhost:4200"

    @property
    def allowed_extensions_list(self) -> list[str]:
        return [ext.strip() for ext in self.ALLOWED_UPLOAD_EXTENSIONS.split(",")]

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",")]


settings = Settings()
