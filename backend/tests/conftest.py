"""Shared test fixtures for backend tests."""

import os

# Override env vars before any app imports
os.environ["DATABASE_URL"] = "postgresql+asyncpg://cortex:cortex_dev@localhost:5432/cortex"
os.environ.setdefault("JWT_SECRET", "test-secret-for-pytest-only")

import pytest  # noqa: E402
from httpx import ASGITransport, AsyncClient  # noqa: E402

from app.main import app  # noqa: E402


@pytest.fixture
async def client() -> AsyncClient:
    """Async HTTP test client."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac  # type: ignore[misc]
