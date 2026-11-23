"""Password hashing, session tokens and CSRF tokens.

Session design (see ADR-013):
- The session is a signed JWT in an httpOnly, SameSite=Lax cookie. JavaScript
  can't read it, so an XSS bug can't steal it directly.
- Each session carries a random CSRF token as a claim. The API returns that token
  in the login and /auth/me response bodies. The frontend sends it back in an
  `X-CSRF-Token` header on every state-changing request. A forged cross-site
  request carries the cookie automatically but can't know the token.
"""

import hmac
import secrets
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError

from app.config import Settings

_hasher = PasswordHasher()  # argon2id with the library's current recommended parameters

# Hash of a random string, used to spend the same time on unknown emails as on
# wrong passwords, so login timing doesn't reveal which emails exist.
_DUMMY_HASH = _hasher.hash(secrets.token_urlsafe(16))


def hash_password(password: str) -> str:
    return _hasher.hash(password)


def verify_password(password: str, password_hash: str | None) -> bool:
    try:
        return _hasher.verify(password_hash or _DUMMY_HASH, password) and password_hash is not None
    except (VerificationError, InvalidHashError):
        return False


def new_csrf_token() -> str:
    return secrets.token_urlsafe(32)


def csrf_tokens_match(expected: str, provided: str | None) -> bool:
    return provided is not None and hmac.compare_digest(expected, provided)


@dataclass(frozen=True)
class SessionClaims:
    user_id: uuid.UUID
    csrf: str


def create_session_token(user_id: uuid.UUID, csrf: str, settings: Settings) -> str:
    now = datetime.now(UTC)
    payload = {
        "sub": str(user_id),
        "csrf": csrf,
        "iat": now,
        "exp": now + timedelta(minutes=settings.jwt_expire_minutes),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_session_token(token: str, settings: Settings) -> SessionClaims | None:
    """Return the claims, or None if the token is invalid, expired or malformed."""
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],  # pinned: never trust the token's own "alg"
            options={"require": ["sub", "csrf", "exp"]},
        )
        return SessionClaims(user_id=uuid.UUID(payload["sub"]), csrf=str(payload["csrf"]))
    except (jwt.PyJWTError, ValueError, KeyError):
        return None
