"""Seed two fictional demo organizations and their demo logins: `make seed`.

Idempotent: running it twice leaves one copy of each org and user. Demo logins
are documented in the README and are for local demos only.

Org A gets the full synthetic dataset and org B a small separate set (Phase 2).
Phase 1 creates only the orgs and users, for the tenant-isolation tests.
"""

import asyncio
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.core.roles import Role
from app.core.security import hash_password
from app.db.models import Organization, User
from app.db.session import get_engine, get_sessionmaker
from app.logging_config import configure_logging, get_logger


@dataclass(frozen=True)
class DemoUser:
    email: str
    full_name: str
    role: Role


@dataclass(frozen=True)
class DemoOrg:
    slug: str
    name: str
    users: tuple[DemoUser, ...]


DEMO_ORGS = (
    DemoOrg(
        slug="kestrel-energy-demo",
        name="Kestrel Energy (fictional demo org A)",
        users=(
            DemoUser("admin@kestrel.example", "Ada Okafor (demo)", Role.ADMIN),
            DemoUser("reviewer@kestrel.example", "Ravi Menon (demo)", Role.REVIEWER),
            DemoUser("engineer@kestrel.example", "Elena Petrova (demo)", Role.ENGINEER),
        ),
    ),
    DemoOrg(
        slug="harrow-petrochem-demo",
        name="Harrow Petrochem (fictional demo org B)",
        users=(
            DemoUser("admin@harrow.example", "Ben Adeyemi (demo)", Role.ADMIN),
            DemoUser("engineer@harrow.example", "Grace Lin (demo)", Role.ENGINEER),
        ),
    ),
)


async def seed_orgs(session: AsyncSession, password: str) -> dict[str, Organization]:
    password_hash = hash_password(password)
    orgs: dict[str, Organization] = {}
    for demo in DEMO_ORGS:
        org = (
            await session.execute(select(Organization).where(Organization.slug == demo.slug))
        ).scalar_one_or_none()
        if org is None:
            org = Organization(slug=demo.slug, name=demo.name)
            session.add(org)
            await session.flush()
        orgs[demo.slug] = org

        for demo_user in demo.users:
            exists = (
                await session.execute(select(User.id).where(User.email == demo_user.email))
            ).scalar_one_or_none()
            if exists is None:
                session.add(
                    User(
                        org_id=org.id,
                        email=demo_user.email,
                        full_name=demo_user.full_name,
                        password_hash=password_hash,
                        role=demo_user.role.value,
                    )
                )
    await session.commit()
    return orgs


async def main() -> None:
    settings = get_settings()
    configure_logging(settings.log_level, json=False)
    log = get_logger("app.seed")
    async with get_sessionmaker()() as session:
        orgs = await seed_orgs(session, settings.demo_password)
    await get_engine().dispose()
    log.info("seed_complete", orgs=[org.name for org in orgs.values()])


if __name__ == "__main__":
    asyncio.run(main())
