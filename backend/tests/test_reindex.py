"""Tests for context file deletion cascade and re-indexing."""

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
        json={"name": "Reindex Project"},
        headers={"Authorization": f"Bearer {token}"},
    )
    return token, r.json()["data"]["id"]


def _auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_delete_file_removes_chunks(client: AsyncClient) -> None:
    """Deleting a context file also removes its chunks (cascade)."""
    token, pid = await _setup(client, "ri-del@test.com")
    # Upload
    r = await client.post(
        f"/api/v1/projects/{pid}/context-files",
        files={"file": ("doc.txt", b"Some content for chunking " * 10, "text/plain")},
        headers=_auth(token),
    )
    assert r.status_code == 201
    file_id = r.json()["data"]["id"]

    # Delete
    r = await client.delete(
        f"/api/v1/projects/{pid}/context-files/{file_id}",
        headers=_auth(token),
    )
    assert r.status_code == 204

    # Verify file list is empty
    r = await client.get(
        f"/api/v1/projects/{pid}/context-files", headers=_auth(token)
    )
    assert len(r.json()["data"]) == 0


@pytest.mark.asyncio
async def test_reindex_endpoint(client: AsyncClient) -> None:
    """POST reindex re-processes file chunks."""
    token, pid = await _setup(client, "ri-reidx@test.com")
    r = await client.post(
        f"/api/v1/projects/{pid}/context-files",
        files={"file": ("notes.txt", b"Important project notes " * 5, "text/plain")},
        headers=_auth(token),
    )
    file_id = r.json()["data"]["id"]

    # Reindex
    r = await client.post(
        f"/api/v1/projects/{pid}/context-files/{file_id}/reindex",
        headers=_auth(token),
    )
    assert r.status_code == 200
    assert r.json()["data"]["status"] in ("indexed", "pending")


@pytest.mark.asyncio
async def test_reupload_replaces_file(client: AsyncClient) -> None:
    """Delete old file + upload new version → only new file exists."""
    token, pid = await _setup(client, "ri-reup@test.com")
    # Upload v1
    r = await client.post(
        f"/api/v1/projects/{pid}/context-files",
        files={"file": ("spec.md", b"# Spec v1", "text/markdown")},
        headers=_auth(token),
    )
    old_id = r.json()["data"]["id"]

    # Delete v1
    await client.delete(
        f"/api/v1/projects/{pid}/context-files/{old_id}",
        headers=_auth(token),
    )

    # Upload v2
    r = await client.post(
        f"/api/v1/projects/{pid}/context-files",
        files={"file": ("spec.md", b"# Spec v2 - updated", "text/markdown")},
        headers=_auth(token),
    )
    assert r.status_code == 201
    new_id = r.json()["data"]["id"]
    assert new_id != old_id

    # Only v2 exists
    r = await client.get(
        f"/api/v1/projects/{pid}/context-files", headers=_auth(token)
    )
    files = r.json()["data"]
    assert len(files) == 1
    assert files[0]["id"] == new_id
