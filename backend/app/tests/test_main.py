import pytest


@pytest.mark.asyncio
async def test_health_endpoint(client):
    response = await client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data
    assert "tools" in data


@pytest.mark.asyncio
async def test_docs_available(client):
    response = await client.get("/docs")
    assert response.status_code == 200
