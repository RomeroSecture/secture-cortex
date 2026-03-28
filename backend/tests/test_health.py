"""Tests for health and status endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient) -> None:
    """GET /health returns ok."""
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_api_status(client: AsyncClient) -> None:
    """GET /api/v1/status returns operational."""
    response = await client.get("/api/v1/status")
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["status"] == "operational"


@pytest.mark.asyncio
async def test_swagger_docs_accessible(client: AsyncClient) -> None:
    """GET /docs returns Swagger UI."""
    response = await client.get("/docs")
    assert response.status_code == 200
    assert "swagger" in response.text.lower()
