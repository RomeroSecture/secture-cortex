"""Indexing pipeline — chunks files, generates embeddings, stores in pgvector."""


import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.context_chunk import ContextChunk
from app.models.context_file import ContextFile, FileStatus
from app.services.chunking import chunk_text
from app.services.embeddings import embed_texts

logger = structlog.get_logger()


async def index_context_file(db: AsyncSession, context_file: ContextFile) -> None:
    """Chunk a context file, embed chunks via Jina, store in pgvector.

    Updates the file status to 'indexed' on success or 'error' on failure.
    """
    file_id = context_file.id
    project_id = context_file.project_id

    # Mark as indexing
    context_file.status = FileStatus.INDEXING
    await db.flush()

    try:
        # Chunk the text
        chunks = chunk_text(context_file.raw_content)
        if not chunks:
            logger.warning("no_chunks_generated", file_id=str(file_id))
            context_file.status = FileStatus.INDEXED
            return

        # Generate embeddings
        embeddings = await embed_texts(chunks)

        # Store chunks with embeddings
        for i, chunk_content in enumerate(chunks):
            embedding = embeddings[i] if i < len(embeddings) else None
            chunk = ContextChunk(
                context_file_id=file_id,
                project_id=project_id,
                chunk_index=i,
                content=chunk_content,
                embedding=embedding,
            )
            db.add(chunk)

        context_file.status = FileStatus.INDEXED
        logger.info(
            "file_indexed",
            file_id=str(file_id),
            chunks=len(chunks),
            embeddings=len(embeddings),
        )

    except Exception:
        context_file.status = FileStatus.ERROR
        logger.exception("indexing_failed", file_id=str(file_id))


async def reindex_context_file(
    db: AsyncSession, context_file: ContextFile
) -> None:
    """Delete old chunks and re-index a context file."""
    from sqlalchemy import delete

    # Guard: pre-fix uploads have placeholder content
    if context_file.raw_content.startswith(
        "[PDF content"
    ) or context_file.raw_content.startswith("[DOCX content"):
        context_file.status = FileStatus.ERROR
        logger.warning(
            "reindex_skipped_placeholder_content",
            file_id=str(context_file.id),
            msg="Uploaded before extraction was implemented. "
            "Delete and re-upload.",
        )
        return

    # Delete existing chunks for this file
    await db.execute(
        delete(ContextChunk).where(
            ContextChunk.context_file_id == context_file.id
        )
    )
    await db.flush()

    # Re-index
    await index_context_file(db, context_file)
