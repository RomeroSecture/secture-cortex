"""Tests for meeting management: start, end, list, get."""

import pytest
from httpx import AsyncClient


async def _setup(client: AsyncClient, email: str) -> tuple[str, str]:
    """Register + create project → (token, project_id)."""
    r = await client.post(
        "/api/v1/auth/register",
        json={"email": email, "name": "T", "password": "securepass123"},
    )
    token = r.json()["data"]["access_token"]
    r = await client.post(
        "/api/v1/projects",
        json={"name": "Meeting Project"},
        headers={"Authorization": f"Bearer {token}"},
    )
    return token, r.json()["data"]["id"]


def _auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_start_meeting(client: AsyncClient) -> None:
    """POST start meeting → status recording + started_at set."""
    token, pid = await _setup(client, "mt-start@test.com")
    r = await client.post(
        f"/api/v1/projects/{pid}/meetings",
        json={"title": "Weekly Client Sync"},
        headers=_auth(token),
    )
    assert r.status_code == 201
    data = r.json()["data"]
    assert data["status"] == "recording"
    assert data["started_at"] is not None
    assert data["ended_at"] is None
    assert data["title"] == "Weekly Client Sync"


@pytest.mark.asyncio
async def test_end_meeting(client: AsyncClient) -> None:
    """POST end meeting → status ended + ended_at set."""
    token, pid = await _setup(client, "mt-end@test.com")
    r = await client.post(
        f"/api/v1/projects/{pid}/meetings",
        json={"title": "Sprint Review"},
        headers=_auth(token),
    )
    meeting_id = r.json()["data"]["id"]

    r = await client.post(
        f"/api/v1/projects/{pid}/meetings/{meeting_id}/end",
        headers=_auth(token),
    )
    assert r.status_code == 200
    data = r.json()["data"]
    assert data["status"] == "ended"
    assert data["ended_at"] is not None


@pytest.mark.asyncio
async def test_end_already_ended_meeting(client: AsyncClient) -> None:
    """Ending an already ended meeting returns 409."""
    token, pid = await _setup(client, "mt-double@test.com")
    r = await client.post(
        f"/api/v1/projects/{pid}/meetings",
        json={},
        headers=_auth(token),
    )
    mid = r.json()["data"]["id"]
    await client.post(f"/api/v1/projects/{pid}/meetings/{mid}/end", headers=_auth(token))

    r = await client.post(f"/api/v1/projects/{pid}/meetings/{mid}/end", headers=_auth(token))
    assert r.status_code == 409


@pytest.mark.asyncio
async def test_list_meetings(client: AsyncClient) -> None:
    """GET meetings returns project meetings."""
    token, pid = await _setup(client, "mt-list@test.com")
    await client.post(
        f"/api/v1/projects/{pid}/meetings",
        json={"title": "Meeting 1"},
        headers=_auth(token),
    )
    await client.post(
        f"/api/v1/projects/{pid}/meetings",
        json={"title": "Meeting 2"},
        headers=_auth(token),
    )
    r = await client.get(f"/api/v1/projects/{pid}/meetings", headers=_auth(token))
    assert r.status_code == 200
    assert len(r.json()["data"]) >= 2


@pytest.mark.asyncio
async def test_get_meeting(client: AsyncClient) -> None:
    """GET single meeting returns detail."""
    token, pid = await _setup(client, "mt-get@test.com")
    r = await client.post(
        f"/api/v1/projects/{pid}/meetings",
        json={"title": "Detail Meeting"},
        headers=_auth(token),
    )
    mid = r.json()["data"]["id"]
    r = await client.get(f"/api/v1/projects/{pid}/meetings/{mid}", headers=_auth(token))
    assert r.status_code == 200
    assert r.json()["data"]["title"] == "Detail Meeting"


@pytest.mark.asyncio
async def test_meeting_non_member_gets_403(client: AsyncClient) -> None:
    """Non-member cannot start meeting in project."""
    token1, pid = await _setup(client, "mt-owner@test.com")
    r = await client.post(
        "/api/v1/auth/register",
        json={"email": "mt-outsider@test.com", "name": "O", "password": "securepass123"},
    )
    token2 = r.json()["data"]["access_token"]
    r = await client.post(
        f"/api/v1/projects/{pid}/meetings",
        json={"title": "Blocked"},
        headers=_auth(token2),
    )
    assert r.status_code == 403
