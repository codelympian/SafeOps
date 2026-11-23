"""Authentication, CSRF and role dependencies shared by every router.

`get_auth` is the single entry point for authenticated requests. It also
enforces CSRF on every state-changing method, so an endpoint can't forget to.
"""

from collections.abc import Awaitable, Callable
from dataclasses import dataclass

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import Settings, get_settings
from app.core.roles import Role
from app.core.security import csrf_tokens_match, decode_session_token
from app.db.models import Organization, User
from app.db.repositories.base import OrgContext
from app.db.session import get_session

SAFE_METHODS = frozenset({"GET", "HEAD", "OPTIONS"})
CSRF_HEADER = "X-CSRF-Token"


@dataclass(frozen=True)
class AuthState:
    user: User
    organization: Organization
    csrf_token: str

    @property
    def ctx(self) -> OrgContext:
        return OrgContext(org_id=self.user.org_id, user_id=self.user.id, role=Role(self.user.role))


def _unauthenticated() -> HTTPException:
    return HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")


async def get_auth(
    request: Request,
    session: AsyncSession = Depends(get_session),
    settings: Settings = Depends(get_settings),
) -> AuthState:
    token = request.cookies.get(settings.session_cookie_name)
    claims = decode_session_token(token, settings) if token else None
    if claims is None:
        raise _unauthenticated()

    if request.method not in SAFE_METHODS and not csrf_tokens_match(
        claims.csrf, request.headers.get(CSRF_HEADER)
    ):
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Missing or invalid CSRF token")

    # Load the user fresh on every request: role changes and deactivation take
    # effect immediately instead of waiting for the token to expire.
    row = (
        await session.execute(
            select(User, Organization)
            .join(Organization, Organization.id == User.org_id)
            .where(User.id == claims.user_id)
        )
    ).one_or_none()
    if row is None or not row.User.is_active:
        raise _unauthenticated()

    return AuthState(user=row.User, organization=row.Organization, csrf_token=claims.csrf)


async def get_org_context(auth: AuthState = Depends(get_auth)) -> OrgContext:
    return auth.ctx


def require_roles(*allowed: Role) -> Callable[..., Awaitable[OrgContext]]:
    """Dependency factory: `ctx: OrgContext = Depends(require_roles(Role.ADMIN))`."""

    async def dependency(ctx: OrgContext = Depends(get_org_context)) -> OrgContext:
        if ctx.role not in allowed:
            raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Insufficient role")
        return ctx

    return dependency
