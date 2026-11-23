from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from redis.asyncio import Redis

from app.api import auth, health, system, users
from app.config import get_settings
from app.core.deps import CSRF_HEADER
from app.db.session import get_engine
from app.logging_config import configure_logging, get_logger
from app.middleware import RequestContextMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    configure_logging(settings.log_level, json=settings.log_json)
    app.state.redis = Redis.from_url(settings.redis_url)
    log = get_logger("app")
    log.info("startup", env=settings.app_env, llm_provider=settings.llm_provider)
    try:
        yield
    finally:
        await app.state.redis.aclose()
        await get_engine().dispose()
        log.info("shutdown")


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="SafeOps Intelligence API",
        version="0.1.0",
        description="HSE document intelligence and pre-job risk decision support. "
        "Advisory only: never a substitute for competent HSE review.",
        lifespan=lifespan,
    )

    for router in (health.router, system.router, auth.router, users.router):
        app.include_router(router)

    # Order matters: the middleware added last runs first. CORS wraps everything,
    # so even error responses carry the right CORS headers.
    app.add_middleware(RequestContextMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Content-Type", CSRF_HEADER, "X-Request-ID"],
        expose_headers=["X-Request-ID"],
    )
    return app


app = create_app()
