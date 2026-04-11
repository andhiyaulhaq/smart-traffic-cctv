import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

@pytest.mark.asyncio
async def test_get_line(client: AsyncClient):
    response = await client.get("/line")
    assert response.status_code == 200
    assert "x1" in response.json()

@pytest.mark.asyncio
async def test_get_events(client: AsyncClient):
    response = await client.get("/events")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
