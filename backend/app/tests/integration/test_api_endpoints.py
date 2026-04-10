import pytest


@pytest.mark.asyncio
async def test_health_check(client):
    response = await client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


@pytest.mark.asyncio
async def test_metadata_invalid_url(client):
    response = await client.post("/api/v1/metadata", json={"url": "not-a-url-at-all"})
    assert response.status_code in (400, 422)


@pytest.mark.asyncio
async def test_metadata_unsupported_platform(client):
    response = await client.post(
        "/api/v1/metadata",
        json={"url": "https://tiktok.com/video/12345"},
    )
    assert response.status_code in (400, 422)


@pytest.mark.asyncio
async def test_download_invalid_url(client):
    response = await client.post("/api/v1/download", json={"url": ""})
    assert response.status_code in (400, 422)


@pytest.mark.asyncio
async def test_history_empty(client):
    response = await client.get("/api/v1/history")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_download_status_not_found(client):
    response = await client.get("/api/v1/download/nonexistent-job-id/status")
    assert response.status_code == 404
