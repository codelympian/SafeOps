from httpx import AsyncClient
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Organization, User
from tests.conftest import TEST_PASSWORD, login, register


async def test_register_creates_org_and_admin_with_httponly_cookie(
    client: AsyncClient, session: AsyncSession
) -> None:
    response = await client.post(
        "/auth/register",
        json={
            "org_name": "Acme Fictional",
            "full_name": "Ada",
            "email": "Ada@Example.com",
            "password": TEST_PASSWORD,
        },
    )
    assert response.status_code == 201
    body = response.json()
    assert body["user"]["role"] == "admin"
    assert body["user"]["email"] == "ada@example.com"  # normalised
    assert body["organization"]["name"] == "Acme Fictional"
    assert body["csrf_token"]
    assert "password_hash" not in response.text

    set_cookie = response.headers["set-cookie"].lower()
    assert "httponly" in set_cookie
    assert "samesite=lax" in set_cookie

    org = (await session.execute(select(Organization))).scalar_one()
    user = (await session.execute(select(User))).scalar_one()
    assert user.org_id == org.id
    assert user.password_hash.startswith("$argon2id$")


async def test_duplicate_email_is_rejected(client: AsyncClient) -> None:
    await register(client, "dup@example.com")
    response = await client.post(
        "/auth/register",
        json={
            "org_name": "Other",
            "full_name": "X",
            "email": "DUP@example.com",
            "password": TEST_PASSWORD,
        },
    )
    assert response.status_code == 409


async def test_short_password_is_rejected(client: AsyncClient) -> None:
    response = await client.post(
        "/auth/register",
        json={"org_name": "O", "full_name": "X", "email": "a@example.com", "password": "short"},
    )
    assert response.status_code == 422


async def test_login_is_case_insensitive_on_email(client: AsyncClient) -> None:
    await register(client, "case@example.com")
    client.cookies.clear()
    await login(client, "CASE@Example.com")
    assert (await client.get("/auth/me")).status_code == 200


async def test_wrong_password_and_unknown_email_look_identical(client: AsyncClient) -> None:
    await register(client, "known@example.com")
    client.cookies.clear()
    wrong = await client.post(
        "/auth/login", json={"email": "known@example.com", "password": "nope-nope-nope"}
    )
    unknown = await client.post(
        "/auth/login", json={"email": "nobody@example.com", "password": "nope-nope-nope"}
    )
    assert wrong.status_code == unknown.status_code == 401
    assert wrong.json() == unknown.json()


async def test_me_requires_a_session(client: AsyncClient) -> None:
    assert (await client.get("/auth/me")).status_code == 401


async def test_tampered_cookie_is_rejected(client: AsyncClient) -> None:
    await register(client, "tamper@example.com")
    token = client.cookies["safeops_session"]
    client.cookies.set("safeops_session", token[:-2] + ("aa" if token[-2:] != "aa" else "bb"))
    assert (await client.get("/auth/me")).status_code == 401


async def test_me_returns_user_org_and_same_csrf_token(client: AsyncClient) -> None:
    csrf = await register(client, "me@example.com", org_name="Me Org")
    body = (await client.get("/auth/me")).json()
    assert body["user"]["email"] == "me@example.com"
    assert body["organization"]["name"] == "Me Org"
    assert body["csrf_token"] == csrf


async def test_write_without_csrf_token_is_forbidden(client: AsyncClient) -> None:
    await register(client, "csrf@example.com")
    assert (await client.post("/auth/logout")).status_code == 403
    assert (await client.post("/auth/logout", headers={"X-CSRF-Token": "wrong"})).status_code == 403


async def test_logout_with_csrf_clears_the_cookie(client: AsyncClient) -> None:
    csrf = await register(client, "bye@example.com")
    response = await client.post("/auth/logout", headers={"X-CSRF-Token": csrf})
    assert response.status_code == 204
    assert "safeops_session" not in client.cookies
    assert (await client.get("/auth/me")).status_code == 401


async def test_deactivated_user_loses_access_immediately(
    client: AsyncClient, session: AsyncSession
) -> None:
    await register(client, "gone@example.com")
    await session.execute(
        update(User).where(User.email == "gone@example.com").values(is_active=False)
    )
    await session.commit()

    assert (await client.get("/auth/me")).status_code == 401  # existing session
    client.cookies.clear()
    response = await client.post(
        "/auth/login", json={"email": "gone@example.com", "password": TEST_PASSWORD}
    )
    assert response.status_code == 401  # new login
