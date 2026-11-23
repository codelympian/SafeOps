"""Application settings, loaded once from environment variables (and .env).

Every tunable lives here so nothing is hardcoded elsewhere. Model IDs in
particular are only ever read from these settings.
"""

from functools import lru_cache
from typing import Annotated, Literal

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict

INSECURE_SECRET = "change-me"  # noqa: S105 - placeholder value we refuse outside development


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        # Backend runs from backend/ on the host, so look one level up for the repo .env.
        env_file=("../.env", ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_env: Literal["development", "test", "production"] = "development"
    log_level: str = "INFO"
    log_json: bool = True

    # NoDecode: skip pydantic-settings' JSON parsing so the validator below can split CSV.
    cors_origins: Annotated[list[str], NoDecode] = Field(
        default_factory=lambda: ["http://localhost:3000"]
    )

    jwt_secret: str = INSECURE_SECRET
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 480
    session_cookie_name: str = "safeops_session"
    cookie_secure: bool = False

    database_url: str = "postgresql+asyncpg://safeops:change-me@localhost:5433/safeops"
    redis_url: str = "redis://localhost:6379/0"

    llm_provider: Literal["mock", "anthropic", "openai"] = "mock"
    llm_model_strong: str = ""
    llm_model_fast: str = ""

    embedding_model: str = "BAAI/bge-small-en-v1.5"

    demo_password: str = "SafeOpsDemo!2026"  # noqa: S105 - documented demo-only login

    @field_validator("cors_origins", mode="before")
    @classmethod
    def _split_origins(cls, value: object) -> object:
        # Allow a comma-separated string in .env: CORS_ORIGINS=http://a,http://b
        if isinstance(value, str) and not value.strip().startswith("["):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value

    @model_validator(mode="after")
    def _refuse_insecure_secret_in_production(self) -> "Settings":
        if self.app_env == "production" and self.jwt_secret == INSECURE_SECRET:
            raise ValueError("JWT_SECRET must be set to a strong value in production")
        if self.app_env == "production" and "*" in self.cors_origins:
            raise ValueError("CORS_ORIGINS must be an explicit allowlist in production")
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
