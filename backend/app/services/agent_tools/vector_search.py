"""Shared pgvector search utilities for agent tools."""

import uuid

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import async_session
from app.models.context_chunk import ContextChunk
from app.services.embeddings import embed_single

logger = structlog.get_logger()


async def search_context_by_query(
    project_id: uuid.UUID,
    query: str,
    top_k: int = 5,
    db: AsyncSession | None = None,
) -> list[str]:
    """Embed a query and search pgvector for the most relevant chunks.

    Returns a list of chunk content strings, sorted by relevance.
    """
    embedding = await embed_single(query)
    if not embedding:
        return []

    async def _search(session: AsyncSession) -> list[str]:
        result = await session.execute(
            select(ContextChunk.content)
            .where(
                ContextChunk.project_id == project_id,
                ContextChunk.embedding.is_not(None),
            )
            .order_by(
                ContextChunk.embedding.cosine_distance(embedding)
            )
            .limit(top_k)
        )
        return [row[0] for row in result.all()]

    if db:
        return await _search(db)

    async with async_session() as session:
        return await _search(session)


async def search_context_by_keyword(
    project_id: uuid.UUID,
    keyword: str,
    top_k: int = 10,
) -> list[str]:
    """Search context chunks by keyword (SQL ILIKE).

    Useful for finding TODO/FIXME markers, specific module names, etc.
    """
    pattern = f"%{keyword}%"
    async with async_session() as session:
        result = await session.execute(
            select(ContextChunk.content)
            .where(
                ContextChunk.project_id == project_id,
                ContextChunk.content.ilike(pattern),
            )
            .limit(top_k)
        )
        return [row[0] for row in result.all()]


async def search_meeting_transcriptions(
    project_id: uuid.UUID,
    query: str,
    top_k: int = 5,
) -> list[str]:
    """Search past meeting transcription chunks via pgvector.

    Transcription chunks have context_file_id = NULL and are
    linked to the project via project_id.
    """
    embedding = await embed_single(query)
    if not embedding:
        return []

    async with async_session() as session:
        result = await session.execute(
            select(ContextChunk.content)
            .where(
                ContextChunk.project_id == project_id,
                ContextChunk.context_file_id.is_(None),
                ContextChunk.embedding.is_not(None),
            )
            .order_by(
                ContextChunk.embedding.cosine_distance(embedding)
            )
            .limit(top_k)
        )
        return [row[0] for row in result.all()]
