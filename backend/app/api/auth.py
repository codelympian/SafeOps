import re
import secrets

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import Settings, get_settings
from app.core.deps import AuthState, get_auth
from app.core.roles import Role
from app.core.security import (
    create_session_token,
    hash_password,
    new_csrf_token,
    verify_password,
)
from app.db.models import Organization, User
from app.db.repositories.users import find_user_by_email_for_login
from app.db.session import get_session
from app.logging_config import get_logger
from app.schemas.auth import LoginRequest, OrgOut, RegisterRequest, SessionOut, UserOut

router = APIRouter(prefix="/auth", tags=["auth"])
_log = get_logger(__name__)


def _slugify(name: str) -> str:
    base = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")[:60] or "org"
    return f"{base}-{secrets.token_hex(3)}"


def _start_session(
    response: Response, user: User, org: Organization, settings: Settings
) -> SessionOut:
    csrf = new_csrf_token()
    response.set_cookie(
        key=settings.session_cookie_name,
        value=create_session_token(user.id, csrf, settings),
        max_age=settings.jwt_expire_minutes * 60,
        httponly=True,
        samesite="lax",
        secure=settings.cookie_secure,
        path="/",
    )
    return SessionOut(
        user=UserOut.model_validate(user),
        organization=OrgOut.model_validate(org),
        csrf_token=csrf,
    )


@router.post("/register", response_model=SessionOut, status_code=status.HTTP_201_CREATED)
async def register(
    body: RegisterRequest,
    response: Response,
    session: AsyncSession = Depends(get_session),
    settings: Settings = Depends(get_settings),
) -> SessionOut:
    """Create a new organization with the caller as its admin (ADR-012)."""
    org = Organization(name=body.org_name, slug=_slugify(body.org_name))
    session.add(org)
    await session.flush()
    user = User(
        org_id=org.id,
        email=body.email,
        full_name=body.full_name,
        password_hash=hash_password(body.password),
        role=Role.ADMIN.value,
    )
    session.add(user)
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, detail="Email already registered") from None
    _log.info("org_registered", org_id=str(org.id), user_id=str(user.id))
    return _start_session(response, user, org, settings)


@router.post("/login", response_model=SessionOut)
async def login(
    body: LoginRequest,
    response: Response,
    session: AsyncSession = Depends(get_session),
    settings: Settings = Depends(get_settings),
) -> SessionOut:
    user = await find_user_by_email_for_login(session, body.email)
    # Always run verify_password, even for unknown emails, so timing doesn't leak existence.
    password_ok = verify_password(body.password, user.password_hash if user else None)
    if user is None or not password_ok or not user.is_active:
        _log.info("login_failed")
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    org = (
        await session.execute(select(Organization).where(Organization.id == user.org_id))
    ).scalar_one()
    _log.info("login_succeeded", user_id=str(user.id), org_id=str(org.id))
    return _start_session(response, user, org, settings)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    response: Response,
    auth: AuthState = Depends(get_auth),
    settings: Settings = Depends(get_settings),
) -> Response:
    response.status_code = status.HTTP_204_NO_CONTENT
    response.delete_cookie(
        settings.session_cookie_name,
        path="/",
        httponly=True,
        samesite="lax",
        secure=settings.cookie_secure,
    )
    _log.info("logout", user_id=str(auth.user.id))
    return response


@router.get("/me", response_model=SessionOut)
async def me(auth: AuthState = Depends(get_auth)) -> SessionOut:
    return SessionOut(
        user=UserOut.model_validate(auth.user),
        organization=OrgOut.model_validate(auth.organization),
        csrf_token=auth.csrf_token,
    )
