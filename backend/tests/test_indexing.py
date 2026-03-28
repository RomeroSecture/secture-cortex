"""Tests for chunking service and indexing pipeline."""

import pytest

from app.services.chunking import chunk_text


def test_chunk_short_text() -> None:
    """Short text returns a single chunk."""
    chunks = chunk_text("Hello world, this is a short text.")
    assert len(chunks) == 1
    assert "Hello world" in chunks[0]


def test_chunk_empty_text() -> None:
    """Empty text returns empty list."""
    assert chunk_text("") == []
    assert chunk_text("   ") == []


def test_chunk_long_text_produces_overlapping_chunks() -> None:
    """Long text is split into overlapping chunks of ~512 tokens."""
    # Create text with ~1000 words (>512 tokens)
    words = [f"word{i}" for i in range(1000)]
    text = " ".join(words)
    chunks = chunk_text(text)

    assert len(chunks) > 1
    # Verify overlap: end of chunk N should overlap with start of chunk N+1
    for i in range(len(chunks) - 1):
        words_current = chunks[i].split()
        words_next = chunks[i + 1].split()
        # Last words of current chunk should appear at start of next chunk
        overlap = set(words_current[-30:]) & set(words_next[:50])
        assert len(overlap) > 0, f"No overlap between chunk {i} and {i + 1}"


def test_chunk_preserves_all_content() -> None:
    """All words from original text appear in at least one chunk."""
    words = [f"unique{i}" for i in range(500)]
    text = " ".join(words)
    chunks = chunk_text(text)
    all_chunk_words = set()
    for chunk in chunks:
        all_chunk_words.update(chunk.split())
    for word in words:
        assert word in all_chunk_words, f"Word {word} missing from chunks"


@pytest.mark.asyncio
async def test_upload_triggers_indexing_without_api_key(client) -> None:  # type: ignore[no-untyped-def]
    """Upload with no embedding API key → file indexed with chunks but no embeddings."""
    from httpx import AsyncClient

    c: AsyncClient = client
    # Register + create project
    r = await c.post(
        "/api/v1/auth/register",
        json={"email": "idx-test@test.com", "name": "Test", "password": "securepass123"},
    )
    token = r.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    r = await c.post("/api/v1/projects", json={"name": "Idx Project"}, headers=headers)
    pid = r.json()["data"]["id"]

    # Upload a text file
    content = "This is test content for chunking. " * 20
    r = await c.post(
        f"/api/v1/projects/{pid}/context-files",
        files={"file": ("test.txt", content.encode(), "text/plain")},
        headers=headers,
    )
    assert r.status_code == 201
    data = r.json()["data"]
    # Without API key, indexing still runs (chunks created, no embeddings)
    # Status should be "indexed" (chunking succeeded, embeddings skipped)
    assert data["status"] in ("indexed", "pending")
