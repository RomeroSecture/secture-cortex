"""RAG pipeline — accumulates transcription, searches context, generates insights.

When AGENT_PIPELINE_ENABLED=true, delegates to the LangGraph multi-agent pipeline.
Otherwise falls back to the legacy single-LLM pipeline.
"""

import uuid
from collections import defaultdict

import structlog
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.context_chunk import ContextChunk
from app.models.insight import Insight, InsightFeedback
from app.services.embeddings import embed_single
from app.services.llm import generate_insight

logger = structlog.get_logger()

# Per-meeting transcription buffer
_buffers: dict[uuid.UUID, list[str]] = defaultdict(list)
# Per-meeting previous insights (for deduplication)
_previous_insights: dict[uuid.UUID, list[str]] = defaultdict(list)

MIN_WORDS = 50
MAX_WORDS = 200


async def add_transcription_and_maybe_generate(
    db: AsyncSession,
    meeting_id: uuid.UUID,
    project_id: uuid.UUID,
    text: str,
    is_final: bool,
    connected_roles: list[str] | None = None,
) -> dict | list[dict] | None:
    """Add transcription text to buffer. When buffer is large enough, run RAG.

    Returns:
      - When agent pipeline enabled: list[dict] (multiple role_insights)
      - When legacy pipeline: dict (single insight) or None
    """
    if not text.strip():
        return None

    _buffers[meeting_id].append(text)
    buffer_text = " ".join(_buffers[meeting_id])
    word_count = len(buffer_text.split())

    if word_count < MIN_WORDS and not (is_final and word_count > 30):
        return None
    if not is_final and word_count < MAX_WORDS:
        return None

    _buffers[meeting_id] = []

    logger.info("rag_triggered", meeting_id=str(meeting_id), words=word_count)

    # Embed and search context (shared by both pipelines)
    query_embedding = await embed_single(buffer_text)
    context_chunks = []
    if query_embedding:
        context_chunks = await _search_context(db, project_id, query_embedding)

    context_texts = [c.content for c in context_chunks]
    feedback_summary = await _get_feedback_summary(db, meeting_id)

    # Route to agent pipeline or legacy
    if settings.agent_pipeline_enabled:
        return await _run_agent_pipeline(
            buffer_text,
            context_texts,
            meeting_id,
            project_id,
            connected_roles=connected_roles,
            feedback_context=feedback_summary,
            context_chunks_raw=context_chunks,
        )

    return await _run_legacy_pipeline(
        buffer_text, context_texts, meeting_id, feedback_summary, context_chunks
    )


async def _run_agent_pipeline(
    buffer_text: str,
    context_texts: list[str],
    meeting_id: uuid.UUID,
    project_id: uuid.UUID,
    connected_roles: list[str] | None = None,
    feedback_context: str = "",
    context_chunks_raw: list | None = None,
) -> list[dict] | None:
    """Run the LangGraph multi-agent pipeline."""
    try:
        from app.services.agent_pipeline import run_pipeline

        insights = await run_pipeline(
            transcription_chunk=buffer_text,
            context_chunks=context_texts,
            meeting_id=meeting_id,
            project_id=project_id,
            connected_roles=connected_roles,
            feedback_context=feedback_context,
            previous_insights=_previous_insights.get(meeting_id),
        )

        if not insights:
            return None

        results = []
        for insight in insights:
            _track_insight(meeting_id, insight.to_legacy_insight())
            results.append(insight.to_legacy_insight())

        return results

    except Exception:
        logger.exception("agent_pipeline_failed_fallback_to_legacy")
        # Graceful degradation: fall back to legacy pipeline
        return await _run_legacy_pipeline(
            buffer_text, context_texts, meeting_id, feedback_context,
            context_chunks_raw or [],
        )


async def _run_legacy_pipeline(
    buffer_text: str,
    context_texts: list[str],
    meeting_id: uuid.UUID,
    feedback_summary: str,
    context_chunks: list,
) -> dict | None:
    """Run the legacy single-LLM pipeline."""
    insight = await generate_insight(
        buffer_text,
        context_texts,
        feedback_context=feedback_summary,
        previous_insights=_previous_insights.get(meeting_id),
    )

    if insight:
        if context_chunks:
            insight["sources"] = [c.content[:100] + "..." for c in context_chunks[:3]]
        _track_insight(meeting_id, insight)

    return insight


def _track_insight(meeting_id: uuid.UUID, insight: dict) -> None:
    """Track insight summary for deduplication in future calls."""
    summary = insight.get("summary", insight.get("content", ""))[:100]
    _previous_insights[meeting_id].append(summary)
    # Keep only last 10
    if len(_previous_insights[meeting_id]) > 10:
        _previous_insights[meeting_id] = _previous_insights[meeting_id][-10:]


async def _search_context(
    db: AsyncSession,
    project_id: uuid.UUID,
    query_embedding: list[float],
    top_k: int = 5,
) -> list[ContextChunk]:
    """Search pgvector for the most relevant context chunks."""
    try:
        result = await db.execute(
            select(ContextChunk)
            .where(
                ContextChunk.project_id == project_id,
                ContextChunk.embedding.is_not(None),
            )
            .order_by(ContextChunk.embedding.cosine_distance(query_embedding))
            .limit(top_k)
        )
        return list(result.scalars().all())
    except Exception:
        logger.exception("pgvector_search_failed")
        return []


async def _get_feedback_summary(db: AsyncSession, meeting_id: uuid.UUID) -> str:
    """Get aggregated feedback context from this meeting's insights."""
    try:
        result = await db.execute(
            select(InsightFeedback.rating, func.count().label("cnt"))
            .join(Insight, Insight.id == InsightFeedback.insight_id)
            .where(Insight.meeting_id == meeting_id)
            .group_by(InsightFeedback.rating)
        )
        rows = result.all()
        if not rows:
            return ""
        parts = [f"{row.rating.value}: {row.cnt}" for row in rows]
        return (
            f"User feedback so far: {', '.join(parts)}. Prioritize useful types."
        )
    except Exception:
        logger.exception("feedback_summary_failed")
        return ""


def clear_buffer(meeting_id: uuid.UUID) -> None:
    """Clear all buffers for a meeting."""
    _buffers.pop(meeting_id, None)
    _previous_insights.pop(meeting_id, None)
