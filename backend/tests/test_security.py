"""Unit tests for hashing, session tokens and settings guards (no database needed)."""

import uuid
from datetime import UTC, datetime, timedelta

import jwt
import pytest
from pydantic import ValidationError

from app.config import Settings
from app.core.security import (
    create_session_token,
    csrf_tokens_match,
    decode_session_token,
    hash_password,
    verify_password,
)

SETTINGS = Settings(jwt_secret="unit-test-secret-0123456789abcdef", app_env="test")


def test_password_hash_is_argon2id_and_verifies() -> None:
    hashed = hash_password("a-long-password")
    assert hashed.startswith("$argon2id$")
    assert verify_password("a-long-password", hashed)
    assert not verify_password("wrong-password", hashed)


def test_verify_password_with_no_hash_is_false() -> None:
    # The unknown-email path: must return False, not raise.
    assert not verify_password("anything", None)


def test_session_token_round_trip() -> None:
    user_id = uuid.uuid4()
    token = create_session_token(user_id, "csrf-abc", SETTINGS)
    claims = decode_session_token(token, SETTINGS)
    assert claims is not None
    assert claims.user_id == user_id
    assert claims.csrf == "csrf-abc"


def test_token_signed_with_another_secret_is_rejected() -> None:
    other = Settings(jwt_secret="a-different-secret-0123456789abcdef", app_env="test")
    token = create_session_token(uuid.uuid4(), "csrf", other)
    assert decode_session_token(token, SETTINGS) is None


def test_expired_token_is_rejected() -> None:
    past = datetime.now(UTC) - timedelta(hours=1)
    token = jwt.encode(
        {"sub": str(uuid.uuid4()), "csrf": "x", "iat": past, "exp": past},
        SETTINGS.jwt_secret,
        algorithm="HS256",
    )
    assert decode_session_token(token, SETTINGS) is None


def test_unsigned_alg_none_token_is_rejected() -> None:
    token = jwt.encode(
        {"sub": str(uuid.uuid4()), "csrf": "x", "exp": datetime.now(UTC) + timedelta(hours=1)},
        key=None,
        algorithm="none",
    )
    assert decode_session_token(token, SETTINGS) is None


def test_garbage_token_is_rejected() -> None:
    assert decode_session_token("not-a-jwt", SETTINGS) is None


def test_csrf_comparison() -> None:
    assert csrf_tokens_match("abc", "abc")
    assert not csrf_tokens_match("abc", "abd")
    assert not csrf_tokens_match("abc", None)


def test_production_refuses_placeholder_secret() -> None:
    with pytest.raises(ValidationError, match="JWT_SECRET"):
        Settings(app_env="production", jwt_secret="change-me")


def test_cors_origins_accepts_comma_separated_string() -> None:
    settings = Settings(cors_origins="http://a.test, http://b.test")
    assert settings.cors_origins == ["http://a.test", "http://b.test"]
