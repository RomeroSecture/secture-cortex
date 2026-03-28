"""Tests for authentication: register and login endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_success(client: AsyncClient) -> None:
    """POST /api/v1/auth/register creates user and returns token."""
    response = await client.post(
        "/api/v1/auth/register",
        json={"email": "test@example.com", "name": "Test User", "password": "securepass123"},
    )
    assert response.status_code == 201
    data = response.json()
    assert "data" in data
    assert data["data"]["token_type"] == "bearer"
    assert data["data"]["access_token"]
    assert data["user"]["email"] == "test@example.com"
    assert data["user"]["name"] == "Test User"
    assert data["user"]["role"] == "developer"
    assert "password" not in data["user"]


@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient) -> None:
    """POST /api/v1/auth/register with duplicate email returns 409."""
    payload = {"email": "dupe@example.com", "name": "User", "password": "securepass123"}
    await client.post("/api/v1/auth/register", json=payload)
    response = await client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_register_weak_password(client: AsyncClient) -> None:
    """POST /api/v1/auth/register with short password returns 422."""
    response = await client.post(
        "/api/v1/auth/register",
        json={"email": "weak@example.com", "name": "User", "password": "short"},
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient) -> None:
    """POST /api/v1/auth/login with valid credentials returns token."""
    await client.post(
        "/api/v1/auth/register",
        json={"email": "login@example.com", "name": "Login User", "password": "securepass123"},
    )
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "login@example.com", "password": "securepass123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["access_token"]
    assert data["user"]["email"] == "login@example.com"


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient) -> None:
    """POST /api/v1/auth/login with wrong password returns 401."""
    await client.post(
        "/api/v1/auth/register",
        json={"email": "wrong@example.com", "name": "User", "password": "securepass123"},
    )
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "wrong@example.com", "password": "wrongpassword"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_login_nonexistent_user(client: AsyncClient) -> None:
    """POST /api/v1/auth/login with unknown email returns 401."""
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "noone@example.com", "password": "anything123"},
    )
    assert response.status_code == 401
