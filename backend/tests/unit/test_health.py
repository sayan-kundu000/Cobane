import pytest
from httpx import AsyncClient


@pytest.mark.anyio
async def test_health_check(client: AsyncClient):
    response = await client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()

    # Assert standard envelope mapping
    assert data["success"] is True
    assert data["data"] == {"status": "operational", "version": "1.0.0"}
    assert "timestamp" in data
    assert "request_id" in data


@pytest.mark.anyio
async def test_health_status(client: AsyncClient):
    response = await client.get("/api/v1/health/status")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "status" in data["data"]
    assert "message" in data["data"]
    assert "logs" in data["data"]


@pytest.mark.anyio
async def test_health_refresh(client: AsyncClient):
    response = await client.post("/api/v1/health/refresh")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "status" in data["data"]
    assert "message" in data["data"]
    assert "logs" in data["data"]
