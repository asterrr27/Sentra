import secrets
import warnings

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./agent_auditor.db"
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"
    JWT_SECRET: str = ""
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:8000"
    RATE_LIMIT: str = "10/minute"
    CUSTOM_AGENT_TIMEOUT: int = 15

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()

if not settings.JWT_SECRET:
    settings.JWT_SECRET = secrets.token_urlsafe(48)
    warnings.warn(
        "JWT_SECRET not set in .env — using a randomly generated secret. "
        "This will change on every restart, invalidating existing tokens."
    )
elif len(settings.JWT_SECRET) < 32:
    raise RuntimeError(
        "JWT_SECRET must be at least 32 characters long. "
        "Run: python -c \"import secrets; print(secrets.token_urlsafe(48))\""
    )
