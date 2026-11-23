import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import require_roles
from app.core.roles import Role
from app.core.security import hash_password
from app.db.models import User
from app.db.repositories.base import OrgContext
from app.db.repositories.users import UserRepository
from app.db.session import get_session
from app.logging_config import get_logger
from app.schemas.auth import CreateUserRequest, UserOut
from app.schemas.errors import error_responses

router = APIRouter(prefix="/users", tags=["users"], responses=error_responses(401, 403))
_log = get_logger(__name__)
admin_only = require_roles(Role.ADMIN)


@router.get("", response_model=list[UserOut])
async def list_users(
    ctx: OrgContext = Depends(admin_only),
    session: AsyncSession = Depends(get_session),
) -> list[UserOut]:
    users = await UserRepository(session, ctx).list()
    return [UserOut.model_validate(user) for user in users]


@router.get("/{user_id}", response_model=UserOut, responses=error_responses(404))
async def get_user(
    user_id: uuid.UUID,
    ctx: OrgContext = Depends(admin_only),
    session: AsyncSession = Depends(get_session),
) -> UserOut:
    user = await UserRepository(session, ctx).get(user_id)
    if user is None:
        # Same response for "doesn't exist" and "belongs to another org", so
        # the API never confirms another tenant's IDs.
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="User not found")
    return UserOut.model_validate(user)


@router.post(
    "", response_model=UserOut, status_code=status.HTTP_201_CREATED, responses=error_responses(409)
)
async def create_user(
    body: CreateUserRequest,
    ctx: OrgContext = Depends(admin_only),
    session: AsyncSession = Depends(get_session),
) -> UserOut:
    """Admins add users to their own organization only."""
    user = UserRepository(session, ctx).add(
        User(
            email=body.email,
            full_name=body.full_name,
            password_hash=hash_password(body.password),
            role=body.role.value,
        )
    )
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, detail="Email already registered") from None
    _log.info("user_created", user_id=str(user.id), role=user.role, by=str(ctx.user_id))
    return UserOut.model_validate(user)
