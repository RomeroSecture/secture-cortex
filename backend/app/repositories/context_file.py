"""Database operations for ContextFile model."""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.context_file import ContextFile, FileStatus


async def create_context_file(
    db: AsyncSession,
    *,
    project_id: uuid.UUID,
    filename: str,
    file_size: int,
    content_type: str,
    raw_content: str,
) -> ContextFile:
    """Store a new context file record."""
    cf = ContextFile(
        project_id=project_id,
        filename=filename,
        file_size=file_size,
        content_type=content_type,
        raw_content=raw_content,
        status=FileStatus.PENDING,
    )
    db.add(cf)
    await db.flush()
    await db.refresh(cf)
    return cf


async def get_context_files_for_project(
    db: AsyncSession, project_id: uuid.UUID
) -> list[ContextFile]:
    """Get all context files for a project."""
    result = await db.execute(
        select(ContextFile)
        .where(ContextFile.project_id == project_id)
        .order_by(ContextFile.created_at.desc())
    )
    return list(result.scalars().all())


async def get_context_file_by_id(
    db: AsyncSession, file_id: uuid.UUID
) -> ContextFile | None:
    """Get a context file by ID."""
    result = await db.execute(select(ContextFile).where(ContextFile.id == file_id))
    return result.scalar_one_or_none()


async def delete_context_file(db: AsyncSession, cf: ContextFile) -> None:
    """Delete a context file."""
    await db.delete(cf)
    await db.flush()
