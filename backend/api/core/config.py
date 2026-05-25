from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # OS env vars (e.g. those set in the Dockerfile) take precedence over .env,
    # so a local .env can point Alembic at the Dockerized Postgres without
    # affecting the container, which gets DB_SERVER=postgres-db from its env.
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    TITLE: str = "Otto Backend"
    VERSION: str = "0.1.0"
    DESCRIPTION: str = "FastAPI backend for Otto, a personal research asssistant"
    API_PREFIX: str = "/api/v1"
    DEBUG: bool = True
    DB_USER: str = ""
    DB_PASSWORD: str = ""
    DB_SERVER: str = ""
    DB_PORT: str = ""
    DB_NAME: str = ""
    SECRET_KEY: str = "8aHsX-TQ}MbI|mS"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 1  # 24 hours
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7  # 7 days
    
settings = Settings()

if settings.DB_NAME:
    DB_ASYNC_CONNECTION_STR=f"postgresql+asyncpg://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_SERVER}:{settings.DB_PORT}/{settings.DB_NAME}"
else:
    DB_ASYNC_CONNECTION_STR = "sqlite+aiosqlite:///./test.db"

PUBLIC_PATHS = [
    "*/openapi.json",
    "*/docs",
    "*/docs/oauth2-redirect",
    "*/login",
    "*/register",
    "*/health",        # Health check endpoint
    "*/public/*",
    "*/event/",
    "/api/v1/",
    "/api/v1/user/register/",
    "/api/v1/user/login/"            # Wildcard support for public endpoints
]

