"""The org-scoped data-access layer.

Every tenant-owned query goes through `OrgScopedRepository`. It adds
`WHERE org_id = :current_org` *inside the SQL*, so rows from another
organization are never loaded at all. Results are never filtered afterwards.
Endpoints never build tenant queries themselves, so the rule is written once.
"""

import uuid
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.roles import Role
from app.db.base import OrgOwnedMixin


@dataclass(frozen=True)
class OrgContext:
    """Who is acting, and in which tenant. Built from the authenticated user only."""

    org_id: uuid.UUID
    user_id: uuid.UUID
    role: Role


class OrgScopedRepository[ModelT: OrgOwnedMixin]:
    model: type[ModelT]

    def __init__(self, session: AsyncSession, ctx: OrgContext) -> None:
        self.session = session
        self.ctx = ctx

    def _select(self) -> Select[ModelT]:
        return select(self.model).where(self.model.org_id == self.ctx.org_id)

    async def get(self, entity_id: uuid.UUID) -> ModelT | None:
        """Fetch by id. A row owned by another org returns None, like a missing row."""
        id_column: Any = self.model.id  # type: ignore[attr-defined]
        result = await self.session.execute(self._select().where(id_column == entity_id))
        return result.scalar_one_or_none()

    async def list(self, *, limit: int = 100, offset: int = 0) -> Sequence[ModelT]:
        result = await self.session.execute(self._select().limit(limit).offset(offset))
        return result.scalars().all()

    def add(self, entity: ModelT) -> ModelT:
        """Stage a new row. org_id is always taken from the context, never from input."""
        entity.org_id = self.ctx.org_id
        self.session.add(entity)
        return entity
