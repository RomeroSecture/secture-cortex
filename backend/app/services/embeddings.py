"""Jina embeddings service — OpenAI-compatible API for vector generation."""

import structlog
from httpx import AsyncClient

from app.config import settings

logger = structlog.get_logger()

# Jina API is OpenAI-compatible: POST /v1/embeddings
JINA_HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {settings.embeddings_api_key}",
}


async def embed_texts(texts: list[str]) -> list[list[float]]:
    """Embed a list of texts using Jina v3 API (1024 dims).

    Returns a list of embedding vectors, one per input text.
    Raises RuntimeError if the API call fails.
    """
    if not settings.embeddings_api_key:
        logger.warning("embeddings_api_key_not_set", msg="Skipping embedding — no API key")
        return []

    url = f"{settings.embeddings_base_url}/embeddings"
    payload = {
        "model": settings.embeddings_model,
        "input": texts,
    }

    async with AsyncClient(timeout=30.0) as client:
        response = await client.post(url, json=payload, headers=JINA_HEADERS)

    if response.status_code != 200:
        logger.error(
            "embedding_api_error",
            status=response.status_code,
            body=response.text[:500],
        )
        msg = f"Embedding API error: {response.status_code}"
        raise RuntimeError(msg)

    data = response.json()
    embeddings = [item["embedding"] for item in data["data"]]
    logger.info("texts_embedded", count=len(texts), dims=len(embeddings[0]) if embeddings else 0)
    return embeddings


async def embed_single(text: str) -> list[float]:
    """Embed a single text string. Returns the embedding vector."""
    results = await embed_texts([text])
    if not results:
        return []
    return results[0]
