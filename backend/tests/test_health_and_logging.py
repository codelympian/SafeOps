from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.main import create_app


async def test_health_reports_database_and_redis(client: AsyncClient) -> None:
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "checks": {"database": "ok", "redis": "ok"}}


async def test_every_response_has_a_request_id(client: AsyncClient) -> None:
    response = await client.get("/system/info")
    assert len(response.headers["x-request-id"]) == 32


async def test_valid_incoming_request_id_is_reused(client: AsyncClient) -> None:
    response = await client.get("/system/info", headers={"X-Request-ID": "trace-1234abcd"})
    assert response.headers["x-request-id"] == "trace-1234abcd"


async def test_unsafe_incoming_request_id_is_replaced(client: AsyncClient) -> None:
    # Header values end up in logs, so anything outside [A-Za-z0-9-] is discarded.
    response = await client.get("/system/info", headers={"X-Request-ID": "bad id\twith-junk"})
    assert response.headers["x-request-id"] != "bad id\twith-junk"


async def test_system_info_reports_mock_mode(client: AsyncClient) -> None:
    body = (await client.get("/system/info")).json()
    assert body["llm_provider"] == "mock"
    assert body["mock_mode"] is True


async def test_unhandled_error_returns_generic_500_without_stack_trace() -> None:
    app: FastAPI = create_app()

    @app.get("/boom")
    async def boom() -> None:
        raise RuntimeError("secret internal detail")

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as c:
        response = await c.get("/boom")

    assert response.status_code == 500
    body = response.json()
    assert body["detail"] == "Internal server error"
    assert body["request_id"] == response.headers["x-request-id"]
    assert "secret internal detail" not in response.text
    assert "Traceback" not in response.text
