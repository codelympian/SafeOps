"""Test setup: a real Postgres test database (never SQLite, never the dev DB).

The test DB URL is the app's DATABASE_URL with the database name swapped to
`safeops_test`, unless TEST_DATABASE_URL is set (CI sets it). Migrations run once
per session (down to base, then up to head), so the migration is tested too.
Each test starts from empty tables.
"""

import os
from collections.abc import AsyncIterator, Iterator

import pytest
from sqlalchemy.engine import make_url

from app.config import Settings, get_settings

_base_url = os.environ.get("TEST_DATABASE_URL") or make_url(Settings().database_url).set(
    database="safeops_test"
).render_as_string(hide_password=False)
os.environ["DATABASE_URL"] = _base_url
os.environ["APP_ENV"] = "test"
os.environ["LOG_JSON"] = "false"
os.environ["JWT_SECRET"] = "test-secret-not-for-production-use-0123456789"
get_settings.cache_clear()

# Imported after the environment is set, so the app reads the test settings.
from alembic.config import Config  # noqa: E402
from httpx import ASGITransport, AsyncClient  # noqa: E402
from redis.asyncio import Redis  # noqa: E402
from sqlalchemy import text  # noqa: E402
from sqlalchemy.ext.asyncio import AsyncSession  # noqa: E402

from alembic import command  # noqa: E402
from app.db.session import get_engine, get_sessionmaker  # noqa: E402
from app.main import app  # noqa: E402

TEST_PASSWORD = "correct-horse-battery"


@pytest.fixture(scope="session", autouse=True)
def _migrated_database() -> Iterator[None]:
    """Sync fixture: Alembic's env.py runs its own event loop via asyncio.run()."""
    config = Config("alembic.ini")
    config.attributes["database_url"] = _base_url
    command.downgrade(config, "base")
    command.upgrade(config, "head")
    yield


@pytest.fixture(autouse=True)
async def _clean_tables() -> AsyncIterator[None]:
    async with get_engine().begin() as conn:
        await conn.execute(text("TRUNCATE organizations, users RESTART IDENTITY CASCADE"))
    yield


@pytest.fixture
async def session() -> AsyncIterator[AsyncSession]:
    async with get_sessionmaker()() as db_session:
        yield db_session


@pytest.fixture(scope="session")
async def _redis() -> AsyncIterator[Redis]:
    client = Redis.from_url(get_settings().redis_url)
    yield client
    await client.aclose()


@pytest.fixture
async def client(_redis: Redis) -> AsyncIterator[AsyncClient]:
    # ASGITransport doesn't run the lifespan, so attach what it would have created.
    app.state.redis = _redis
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as c:
        yield c


async def register(
    client: AsyncClient, email: str, org_name: str = "Test Org", password: str = TEST_PASSWORD
) -> str:
    """Register a new org + admin. The client keeps the session cookie. Returns the CSRF token."""
    response = await client.post(
        "/auth/register",
        json={
            "org_name": org_name,
            "full_name": "Test Admin",
            "email": email,
            "password": password,
        },
    )
    assert response.status_code == 201, response.text
    return str(response.json()["csrf_token"])


async def login(client: AsyncClient, email: str, password: str = TEST_PASSWORD) -> str:
    response = await client.post("/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200, response.text
    return str(response.json()["csrf_token"])
