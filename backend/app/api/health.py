import asyncio
from typing import Literal

from fastapi import APIRouter, Request, Response, status
from pydantic import BaseModel
from sqlalchemy import text

from app.db.session import get_engine
from app.logging_config import get_logger

router = APIRouter(tags=["health"])
_log = get_logger(__name__)
_TIMEOUT_SECONDS = 2.0

CheckStatus = Literal["ok", "error"]


class HealthOut(BaseModel):
    status: CheckStatus
    checks: dict[str, CheckStatus]


async def _check_database() -> CheckStatus:
    try:
        async with asyncio.timeout(_TIMEOUT_SECONDS):
            async with get_engine().connect() as conn:
                await conn.execute(text("SELECT 1"))
        return "ok"
    except Exception as exc:
        _log.warning("health_check_failed", dependency="database", error=type(exc).__name__)
        return "error"


async def _check_redis(request: Request) -> CheckStatus:
    try:
        async with asyncio.timeout(_TIMEOUT_SECONDS):
            await request.app.state.redis.ping()
        return "ok"
    except Exception as exc:
        _log.warning("health_check_failed", dependency="redis", error=type(exc).__name__)
        return "error"


@router.get(
    "/health",
    response_model=HealthOut,
    responses={503: {"model": HealthOut, "description": "A dependency is unavailable"}},
)
async def health(request: Request, response: Response) -> HealthOut:
    database, redis = await asyncio.gather(_check_database(), _check_redis(request))
    checks: dict[str, CheckStatus] = {"database": database, "redis": redis}
    healthy = all(value == "ok" for value in checks.values())
    if not healthy:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    return HealthOut(status="ok" if healthy else "error", checks=checks)
