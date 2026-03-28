"""Tests for project access control and multi-tenancy isolation."""

import pytest
from httpx import AsyncClient


async def _register(client: AsyncClient, email: str) -> dict:
    """Helper: register and return {token, user_id}."""
    r = await client.post(
        "/api/v1/auth/register",
        json={"email": email, "name": "Test", "password": "securepass123"},
    )
    data = r.json()
    return {"token": data["data"]["access_token"], "user_id": data["user"]["id"]}


def _auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_admin_assigns_user_to_project(client: AsyncClient) -> None:
    """Admin can assign another user to a project with a role."""
    admin = await _register(client, "ac-admin@test.com")
    dev = await _register(client, "ac-dev@test.com")

    # Admin creates project
    r = await client.post(
        "/api/v1/projects",
        json={"name": "AC Project"},
        headers=_auth(admin["token"]),
    )
    project_id = r.json()["data"]["id"]

    # Admin assigns dev
    r = await client.post(
        f"/api/v1/projects/{project_id}/members",
        json={"user_id": dev["user_id"], "role": "developer"},
        headers=_auth(admin["token"]),
    )
    assert r.status_code == 201
    members = r.json()["data"]
    assert len(members) == 2
    roles = {m["role_in_project"] for m in members}
    assert "admin" in roles
    assert "developer" in roles


@pytest.mark.asyncio
async def test_assigned_user_can_access_project(client: AsyncClient) -> None:
    """A user assigned to a project can access it."""
    admin = await _register(client, "ac-owner2@test.com")
    member = await _register(client, "ac-member2@test.com")

    r = await client.post(
        "/api/v1/projects",
        json={"name": "Shared Project"},
        headers=_auth(admin["token"]),
    )
    project_id = r.json()["data"]["id"]

    # Assign member
    await client.post(
        f"/api/v1/projects/{project_id}/members",
        json={"user_id": member["user_id"], "role": "developer"},
        headers=_auth(admin["token"]),
    )

    # Member can access
    r = await client.get(f"/api/v1/projects/{project_id}", headers=_auth(member["token"]))
    assert r.status_code == 200

    # Member appears in project list
    r = await client.get("/api/v1/projects", headers=_auth(member["token"]))
    project_ids = [p["id"] for p in r.json()["data"]]
    assert project_id in project_ids


@pytest.mark.asyncio
async def test_non_member_gets_403(client: AsyncClient) -> None:
    """A user NOT assigned to a project gets 403 Forbidden."""
    admin = await _register(client, "ac-owner3@test.com")
    outsider = await _register(client, "ac-outsider3@test.com")

    r = await client.post(
        "/api/v1/projects",
        json={"name": "Private Project"},
        headers=_auth(admin["token"]),
    )
    project_id = r.json()["data"]["id"]

    r = await client.get(f"/api/v1/projects/{project_id}", headers=_auth(outsider["token"]))
    assert r.status_code == 403


@pytest.mark.asyncio
async def test_data_isolation_between_projects(client: AsyncClient) -> None:
    """Data from project A is never visible in project B queries."""
    user_a = await _register(client, "ac-usera@test.com")
    user_b = await _register(client, "ac-userb@test.com")

    # Each user creates their own project
    r = await client.post(
        "/api/v1/projects",
        json={"name": "Project A"},
        headers=_auth(user_a["token"]),
    )
    project_a_id = r.json()["data"]["id"]

    r = await client.post(
        "/api/v1/projects",
        json={"name": "Project B"},
        headers=_auth(user_b["token"]),
    )
    project_b_id = r.json()["data"]["id"]

    # User A only sees Project A
    r = await client.get("/api/v1/projects", headers=_auth(user_a["token"]))
    ids_a = [p["id"] for p in r.json()["data"]]
    assert project_a_id in ids_a
    assert project_b_id not in ids_a

    # User B only sees Project B
    r = await client.get("/api/v1/projects", headers=_auth(user_b["token"]))
    ids_b = [p["id"] for p in r.json()["data"]]
    assert project_b_id in ids_b
    assert project_a_id not in ids_b

    # User A cannot access Project B
    r = await client.get(f"/api/v1/projects/{project_b_id}", headers=_auth(user_a["token"]))
    assert r.status_code == 403


@pytest.mark.asyncio
async def test_non_admin_cannot_assign_members(client: AsyncClient) -> None:
    """A developer cannot assign members to a project."""
    admin = await _register(client, "ac-admin5@test.com")
    dev = await _register(client, "ac-dev5@test.com")
    new_user = await _register(client, "ac-new5@test.com")

    r = await client.post(
        "/api/v1/projects",
        json={"name": "Restricted"},
        headers=_auth(admin["token"]),
    )
    project_id = r.json()["data"]["id"]

    # Assign dev as developer
    await client.post(
        f"/api/v1/projects/{project_id}/members",
        json={"user_id": dev["user_id"], "role": "developer"},
        headers=_auth(admin["token"]),
    )

    # Dev tries to assign new_user → 403
    r = await client.post(
        f"/api/v1/projects/{project_id}/members",
        json={"user_id": new_user["user_id"], "role": "developer"},
        headers=_auth(dev["token"]),
    )
    assert r.status_code == 403
