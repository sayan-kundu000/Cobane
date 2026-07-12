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
