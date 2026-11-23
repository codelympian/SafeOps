"""Tenant isolation: org A must never read or write org B's data.

Phase 1 covers users, the only tenant-owned table so far. Later phases add the
same checks for documents, chunks/retrieval, incidents, assessments,
conversations and citations.
"""

from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.core.roles import Role
from app.db.models import User
from app.db.repositories.base import OrgContext
from app.db.repositories.users import UserRepository
from app.seed import seed_orgs
from tests.conftest import TEST_PASSWORD, login

ORG_A_ADMIN = "admin@kestrel.example"
ORG_B_ADMIN = "admin@harrow.example"


async def _seed(session: AsyncSession) -> None:
    await seed_orgs(session, get_settings().demo_password)


async def _user(session: AsyncSession, email: str) -> User:
    return (await session.execute(select(User).where(User.email == email))).scalar_one()


async def test_repository_never_returns_another_orgs_rows(session: AsyncSession) -> None:
    await _seed(session)
    admin_a = await _user(session, ORG_A_ADMIN)
    admin_b = await _user(session, ORG_B_ADMIN)
    repo_a = UserRepository(session, OrgContext(admin_a.org_id, admin_a.id, Role.ADMIN))

    assert await repo_a.get(admin_b.id) is None
    listed = await repo_a.list()
    assert listed, "org A should see its own users"
    assert {user.org_id for user in listed} == {admin_a.org_id}


async def test_repository_add_forces_the_callers_org(session: AsyncSession) -> None:
    await _seed(session)
    admin_a = await _user(session, ORG_A_ADMIN)
    admin_b = await _user(session, ORG_B_ADMIN)
    repo_a = UserRepository(session, OrgContext(admin_a.org_id, admin_a.id, Role.ADMIN))

    sneaky = User(
        org_id=admin_b.org_id,  # an attempt to write into org B
        email="sneaky@example.com",
        full_name="Sneaky",
        password_hash="x",
        role="engineer",
    )
    repo_a.add(sneaky)
    await session.commit()
    assert sneaky.org_id == admin_a.org_id


async def test_api_list_shows_only_own_org(client: AsyncClient, session: AsyncSession) -> None:
    await _seed(session)
    await login(client, ORG_A_ADMIN, get_settings().demo_password)
    emails = {user["email"] for user in (await client.get("/users")).json()}
    assert emails == {
        "admin@kestrel.example",
        "reviewer@kestrel.example",
        "engineer@kestrel.example",
    }


async def test_api_get_other_orgs_user_is_404_not_403(
    client: AsyncClient, session: AsyncSession
) -> None:
    await _seed(session)
    org_b_user = await _user(session, ORG_B_ADMIN)
    await login(client, ORG_A_ADMIN, get_settings().demo_password)

    response = await client.get(f"/users/{org_b_user.id}")
    # 404, not 403: the API must not even confirm that the ID exists.
    assert response.status_code == 404


async def test_api_create_ignores_org_id_in_body(
    client: AsyncClient, session: AsyncSession
) -> None:
    await _seed(session)
    org_a_id = (await _user(session, ORG_A_ADMIN)).org_id
    org_b_id = (await _user(session, ORG_B_ADMIN)).org_id
    csrf = await login(client, ORG_A_ADMIN, get_settings().demo_password)

    response = await client.post(
        "/users",
        headers={"X-CSRF-Token": csrf},
        json={
            "full_name": "Injected",
            "email": "injected@example.com",
            "password": TEST_PASSWORD,
            "role": "engineer",
            "org_id": str(org_b_id),
        },
    )
    assert response.status_code == 201
    created = await _user(session, "injected@example.com")
    assert created.org_id == org_a_id


async def test_seed_is_idempotent(session: AsyncSession) -> None:
    await _seed(session)
    await _seed(session)
    users = (await session.execute(select(User))).scalars().all()
    assert len(users) == 5
