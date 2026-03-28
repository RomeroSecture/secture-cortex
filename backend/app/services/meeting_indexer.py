"""Meeting indexer — embeds meeting transcription into pgvector for cumulative context."""

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.context_chunk import ContextChunk
from app.models.meeting import Meeting
from app.models.transcription import Transcription
from app.services.chunking import chunk_text
from app.services.embeddings import embed_texts

logger = structlog.get_logger()


async def index_meeting_transcription(db: AsyncSession, meeting: Meeting) -> None:
    """Embed the full transcription of a meeting and store as context chunks.

    This enables the RAG pipeline to search through past meeting content
    when generating insights in future meetings (cumulative memory).
    """
    # Fetch all transcription segments
    result = await db.execute(
        select(Transcription)
        .where(Transcription.meeting_id == meeting.id)
        .order_by(Transcription.timestamp)
    )
    segments = list(result.scalars().all())

    if not segments:
        logger.info("no_transcription_to_index", meeting_id=str(meeting.id))
        return

    # Combine segments into full text
    full_text = "\n".join(f"{s.speaker}: {s.text}" for s in segments)

    # Chunk and embed
    chunks = chunk_text(full_text)
    if not chunks:
        return

    embeddings = await embed_texts(chunks)

    # Store as context chunks linked to the project (not a context_file)
    for i, content in enumerate(chunks):
        embedding = embeddings[i] if i < len(embeddings) else None
        chunk = ContextChunk(
            context_file_id=None,  # No file — from meeting transcription
            project_id=meeting.project_id,
            chunk_index=i,
            content=f"[Meeting: {meeting.title}] {content}",
            embedding=embedding,
        )
        db.add(chunk)

    logger.info(
        "meeting_transcription_indexed",
        meeting_id=str(meeting.id),
        chunks=len(chunks),
    )
