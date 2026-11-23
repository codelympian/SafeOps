from httpx import AsyncClient

from tests.conftest import TEST_PASSWORD, login, register


async def _admin_creates(client: AsyncClient, csrf: str, email: str, role: str) -> None:
    response = await client.post(
        "/users",
        headers={"X-CSRF-Token": csrf},
        json={"full_name": "New User", "email": email, "password": TEST_PASSWORD, "role": role},
    )
    assert response.status_code == 201, response.text
    assert response.json()["role"] == role


async def test_admin_can_add_users_who_can_then_log_in(client: AsyncClient) -> None:
    csrf = await register(client, "boss@example.com")
    await _admin_creates(client, csrf, "rev@example.com", "reviewer")

    client.cookies.clear()
    await login(client, "rev@example.com")
    me = (await client.get("/auth/me")).json()
    assert me["user"]["role"] == "reviewer"


async def test_engineer_and_reviewer_cannot_manage_users(client: AsyncClient) -> None:
    csrf = await register(client, "boss2@example.com")
    await _admin_creates(client, csrf, "eng@example.com", "engineer")
    await _admin_creates(client, csrf, "rev2@example.com", "reviewer")

    for email in ("eng@example.com", "rev2@example.com"):
        client.cookies.clear()
        user_csrf = await login(client, email)
        assert (await client.get("/users")).status_code == 403
        response = await client.post(
            "/users",
            headers={"X-CSRF-Token": user_csrf},
            json={
                "full_name": "X",
                "email": f"x-{email}",
                "password": TEST_PASSWORD,
                "role": "admin",
            },
        )
        assert response.status_code == 403


async def test_unknown_role_is_rejected(client: AsyncClient) -> None:
    csrf = await register(client, "boss3@example.com")
    response = await client.post(
        "/users",
        headers={"X-CSRF-Token": csrf},
        json={
            "full_name": "X",
            "email": "x@example.com",
            "password": TEST_PASSWORD,
            "role": "superuser",
        },
    )
    assert response.status_code == 422
