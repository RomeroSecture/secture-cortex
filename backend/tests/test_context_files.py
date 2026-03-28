"""Tests for context file upload and management."""

import pytest
from httpx import AsyncClient


async def _setup_project(client: AsyncClient, email: str) -> tuple[str, str]:
    """Helper: register user, create project, return (token, project_id)."""
    r = await client.post(
        "/api/v1/auth/register",
        json={"email": email, "name": "Test", "password": "securepass123"},
    )
    token = r.json()["data"]["access_token"]
    r = await client.post(
        "/api/v1/projects",
        json={"name": "Context Project"},
        headers={"Authorization": f"Bearer {token}"},
    )
    project_id = r.json()["data"]["id"]
    return token, project_id


def _auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_upload_text_file(client: AsyncClient) -> None:
    """Upload a .txt file → stored with name, size, status pending."""
    token, pid = await _setup_project(client, "cf-upload@test.com")
    response = await client.post(
        f"/api/v1/projects/{pid}/context-files",
        files={"file": ("architecture.txt", b"FastAPI + PostgreSQL stack", "text/plain")},
        headers=_auth(token),
    )
    assert response.status_code == 201
    data = response.json()["data"]
    assert data["filename"] == "architecture.txt"
    assert data["file_size"] == len(b"FastAPI + PostgreSQL stack")
    assert data["status"] in ("indexed", "pending")  # indexed if chunking runs


@pytest.mark.asyncio
async def test_upload_markdown_file(client: AsyncClient) -> None:
    """Upload a .md file → stored correctly."""
    token, pid = await _setup_project(client, "cf-md@test.com")
    content = b"# Architecture\n\nThis is the project architecture."
    response = await client.post(
        f"/api/v1/projects/{pid}/context-files",
        files={"file": ("readme.md", content, "text/markdown")},
        headers=_auth(token),
    )
    assert response.status_code == 201
    assert response.json()["data"]["filename"] == "readme.md"


@pytest.mark.asyncio
async def test_upload_unsupported_type(client: AsyncClient) -> None:
    """Upload a .exe file → 422 unsupported."""
    token, pid = await _setup_project(client, "cf-bad@test.com")
    response = await client.post(
        f"/api/v1/projects/{pid}/context-files",
        files={"file": ("malware.exe", b"MZ...", "application/octet-stream")},
        headers=_auth(token),
    )
    assert response.status_code == 422
    assert "Unsupported" in response.json()["error"]["message"]


@pytest.mark.asyncio
async def test_upload_file_too_large(client: AsyncClient) -> None:
    """Upload a file > 10MB → 422 too large."""
    token, pid = await _setup_project(client, "cf-big@test.com")
    big_content = b"x" * (11 * 1024 * 1024)  # 11MB
    response = await client.post(
        f"/api/v1/projects/{pid}/context-files",
        files={"file": ("huge.txt", big_content, "text/plain")},
        headers=_auth(token),
    )
    assert response.status_code == 422
    assert "too large" in response.json()["error"]["message"].lower()


@pytest.mark.asyncio
async def test_list_context_files(client: AsyncClient) -> None:
    """List context files for a project."""
    token, pid = await _setup_project(client, "cf-list@test.com")
    await client.post(
        f"/api/v1/projects/{pid}/context-files",
        files={"file": ("file1.txt", b"content1", "text/plain")},
        headers=_auth(token),
    )
    await client.post(
        f"/api/v1/projects/{pid}/context-files",
        files={"file": ("file2.json", b'{"key": "value"}', "application/json")},
        headers=_auth(token),
    )
    response = await client.get(
        f"/api/v1/projects/{pid}/context-files", headers=_auth(token)
    )
    assert response.status_code == 200
    files = response.json()["data"]
    assert len(files) == 2
    names = {f["filename"] for f in files}
    assert "file1.txt" in names
    assert "file2.json" in names


@pytest.mark.asyncio
async def test_delete_context_file(client: AsyncClient) -> None:
    """Delete a context file removes it."""
    token, pid = await _setup_project(client, "cf-del@test.com")
    r = await client.post(
        f"/api/v1/projects/{pid}/context-files",
        files={"file": ("to-delete.txt", b"bye", "text/plain")},
        headers=_auth(token),
    )
    file_id = r.json()["data"]["id"]
    response = await client.delete(
        f"/api/v1/projects/{pid}/context-files/{file_id}", headers=_auth(token)
    )
    assert response.status_code == 204
    # Verify gone
    r = await client.get(f"/api/v1/projects/{pid}/context-files", headers=_auth(token))
    assert len(r.json()["data"]) == 0
