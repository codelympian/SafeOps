from app.worker.settings import WorkerSettings, ping


async def test_ping_task_returns_pong() -> None:
    assert await ping({"job_id": "test"}) == "pong"


def test_worker_registers_ping() -> None:
    assert ping in WorkerSettings.functions
