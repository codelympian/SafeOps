from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import User
from app.db.repositories.base import OrgScopedRepository


class UserRepository(OrgScopedRepository[User]):
    """Users inside the caller's organization."""

    model = User


async def find_user_by_email_for_login(session: AsyncSession, email: str) -> User | None:
    """The one deliberately unscoped user lookup.

    At login we don't know the org yet. This returns only the matching user's
    own row, and is used solely to verify credentials.
    """
    result = await session.execute(select(User).where(User.email == email.lower()))
    return result.scalar_one_or_none()
