"""Arq worker entry point: `arq app.worker.settings.WorkerSettings`.

Phase 1 has a single `ping` task to prove the queue round-trips. Ingestion and
extraction tasks are added in Phases 2 and 5. Heavy work always runs here,
never inside an API request.
"""

from typing import Any, ClassVar

from arq.connections import RedisSettings

from app.config import get_settings
from app.logging_config import configure_logging, get_logger

_log = get_logger("app.worker")


async def ping(ctx: dict[str, Any]) -> str:
    _log.info("task_ping", job_id=ctx.get("job_id"))
    return "pong"


async def startup(ctx: dict[str, Any]) -> None:
    settings = get_settings()
    configure_logging(settings.log_level, json=settings.log_json)
    # Phase 2: load the embedding model here, once per worker process.
    _log.info("worker_startup", env=settings.app_env)


async def shutdown(ctx: dict[str, Any]) -> None:
    _log.info("worker_shutdown")


class WorkerSettings:
    functions: ClassVar[list[Any]] = [ping]
    on_startup = startup
    on_shutdown = shutdown
    redis_settings = RedisSettings.from_dsn(get_settings().redis_url)
    max_jobs = 4
    job_timeout = 600
