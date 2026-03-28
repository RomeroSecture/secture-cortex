"""Tests for project CRUD endpoints."""

import pytest
from httpx import AsyncClient


async def _register_and_get_token(client: AsyncClient, email: str) -> str:
    """Helper: register a user and return the JWT token."""
    r = await client.post(
        "/api/v1/auth/register",
        json={"email": email, "name": "Test", "password": "securepass123"},
    )
    return r.json()["data"]["access_token"]


def _auth(token: str) -> dict[str, str]:
    """Helper: Authorization header."""
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_create_project(client: AsyncClient) -> None:
    """POST /api/v1/projects creates project and auto-assigns admin."""
    token = await _register_and_get_token(client, "proj-create@test.com")
    response = await client.post(
        "/api/v1/projects",
        json={"name": "LaLiga Fantasy", "description": "Client project"},
        headers=_auth(token),
    )
    assert response.status_code == 201
    data = response.json()["data"]
    assert data["name"] == "LaLiga Fantasy"
    assert data["description"] == "Client project"
    assert "id" in data


@pytest.mark.asyncio
async def test_list_projects(client: AsyncClient) -> None:
    """GET /api/v1/projects returns user's projects."""
    token = await _register_and_get_token(client, "proj-list@test.com")
    await client.post(
        "/api/v1/projects",
        json={"name": "Project A"},
        headers=_auth(token),
    )
    await client.post(
        "/api/v1/projects",
        json={"name": "Project B"},
        headers=_auth(token),
    )
    response = await client.get("/api/v1/projects", headers=_auth(token))
    assert response.status_code == 200
    projects = response.json()["data"]
    assert len(projects) >= 2
    names = [p["name"] for p in projects]
    assert "Project A" in names
    assert "Project B" in names


@pytest.mark.asyncio
async def test_get_project(client: AsyncClient) -> None:
    """GET /api/v1/projects/{id} returns project detail."""
    token = await _register_and_get_token(client, "proj-get@test.com")
    create_resp = await client.post(
        "/api/v1/projects",
        json={"name": "Detail Project"},
        headers=_auth(token),
    )
    project_id = create_resp.json()["data"]["id"]
    response = await client.get(f"/api/v1/projects/{project_id}", headers=_auth(token))
    assert response.status_code == 200
    assert response.json()["data"]["name"] == "Detail Project"


@pytest.mark.asyncio
async def test_update_project(client: AsyncClient) -> None:
    """PATCH /api/v1/projects/{id} updates project fields."""
    token = await _register_and_get_token(client, "proj-update@test.com")
    create_resp = await client.post(
        "/api/v1/projects",
        json={"name": "Old Name", "description": "Old desc"},
        headers=_auth(token),
    )
    project_id = create_resp.json()["data"]["id"]
    response = await client.patch(
        f"/api/v1/projects/{project_id}",
        json={"name": "New Name"},
        headers=_auth(token),
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["name"] == "New Name"
    assert data["description"] == "Old desc"  # unchanged


@pytest.mark.asyncio
async def test_delete_project(client: AsyncClient) -> None:
    """DELETE /api/v1/projects/{id} removes project."""
    token = await _register_and_get_token(client, "proj-delete@test.com")
    create_resp = await client.post(
        "/api/v1/projects",
        json={"name": "To Delete"},
        headers=_auth(token),
    )
    project_id = create_resp.json()["data"]["id"]
    response = await client.delete(f"/api/v1/projects/{project_id}", headers=_auth(token))
    assert response.status_code == 204
    # Verify it's gone
    get_resp = await client.get(f"/api/v1/projects/{project_id}", headers=_auth(token))
    assert get_resp.status_code == 403  # no longer a member (project deleted)


@pytest.mark.asyncio
async def test_project_access_denied_for_non_member(client: AsyncClient) -> None:
    """GET /api/v1/projects/{id} returns 403 for non-members."""
    token1 = await _register_and_get_token(client, "proj-owner@test.com")
    token2 = await _register_and_get_token(client, "proj-outsider@test.com")
    create_resp = await client.post(
        "/api/v1/projects",
        json={"name": "Private Project"},
        headers=_auth(token1),
    )
    project_id = create_resp.json()["data"]["id"]
    response = await client.get(f"/api/v1/projects/{project_id}", headers=_auth(token2))
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_create_project_unauthenticated(client: AsyncClient) -> None:
    """POST /api/v1/projects without token returns 401."""
    response = await client.post("/api/v1/projects", json={"name": "No Auth"})
    assert response.status_code == 401
