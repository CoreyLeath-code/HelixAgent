"""Contract tests for the HelixAgent FastAPI service."""

import pytest
from httpx import ASGITransport, AsyncClient

from api.main import app


@pytest.mark.asyncio
async def test_root_contract() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "HelixAgent"}


@pytest.mark.asyncio
async def test_health_contract() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    assert "version" in response.json()


@pytest.mark.asyncio
async def test_predict_fallback_contract() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/predict", json={"prompt": "summarize system health"})

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data["result"], str)
    assert data["result"]


@pytest.mark.asyncio
async def test_predict_rejects_missing_prompt() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/predict", json={})

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_and_read_autonomous_run() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        created = await client.post("/runs", json={"objective": "Summarize system health"})
        assert created.status_code == 202
        run_id = created.json()["id"]

        fetched = await client.get(f"/runs/{run_id}")

    assert fetched.status_code == 200
    assert fetched.json()["status"] == "completed"


@pytest.mark.asyncio
async def test_unknown_run_returns_404() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/runs/not-a-run")

    assert response.status_code == 404
