"""Context file upload and management endpoints."""

import asyncio
import uuid
from typing import Annotated

import structlog
from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.repositories.context_file import (
    create_context_file,
    delete_context_file,
    get_context_file_by_id,
    get_context_files_for_project,
)
from app.repositories.project import get_user_project_role
from app.schemas.context_file import (
    ContextFileDetailResponse,
    ContextFileListResponse,
    ContextFileResponse,
)
from app.services.indexing import index_context_file, reindex_context_file

logger = structlog.get_logger()

router = APIRouter(prefix="/projects/{project_id}/context-files", tags=["context"])

ALLOWED_TYPES = {
    "text/plain",
    "text/markdown",
    "text/csv",
    "application/json",
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}
ALLOWED_EXTENSIONS = {".txt", ".md", ".csv", ".json", ".pdf", ".docx"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


def _validate_file(file: UploadFile) -> None:
    """Validate file type and extension."""
    if file.filename is None:
        raise HTTPException(status_code=422, detail="Filename is required")
    ext = "." + file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=422,
            detail=f"Unsupported file type. Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}",
        )


def _validate_binary_content(
    content: bytes, filename: str,
) -> None:
    """Validate that binary content matches the expected file type."""
    ext = (
        filename.rsplit(".", 1)[-1].lower()
        if "." in filename
        else ""
    )
    if ext == "pdf" and content[:5] != b"%PDF-":
        raise HTTPException(
            status_code=422,
            detail="File content does not match PDF format",
        )
    if ext == "docx" and content[:4] != b"PK\x03\x04":
        raise HTTPException(
            status_code=422,
            detail="File content does not match DOCX format",
        )


async def _extract_text(content: bytes, filename: str) -> str:
    """Extract text content from supported file types.

    PDF and DOCX extraction runs in a thread to avoid blocking
    the event loop (CPU-bound work).
    """
    ext = (
        filename.rsplit(".", 1)[-1].lower()
        if "." in filename
        else ""
    )
    if ext in ("txt", "md", "csv", "json"):
        return content.decode("utf-8", errors="replace")
    if ext == "pdf":
        from app.services.extraction import extract_pdf_text

        text = await asyncio.to_thread(extract_pdf_text, content)
        if not text:
            logger.warning(
                "pdf_extraction_empty", filename=filename,
            )
        return text
    if ext == "docx":
        from app.services.extraction import extract_docx_text

        text = await asyncio.to_thread(extract_docx_text, content)
        if not text:
            logger.warning(
                "docx_extraction_empty", filename=filename,
            )
        return text
    return ""


@router.post("", response_model=ContextFileDetailResponse, status_code=status.HTTP_201_CREATED)
async def upload_context_file(
    project_id: uuid.UUID,
    file: UploadFile,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> ContextFileDetailResponse:
    """Upload a context file to a project's knowledge base."""
    role = await get_user_project_role(db, project_id, current_user.id)
    if role is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not a project member")
    _validate_file(file)
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"File too large. Maximum size is {MAX_FILE_SIZE // (1024 * 1024)}MB",
        )
    _validate_binary_content(content, file.filename or "")
    raw_text = await _extract_text(content, file.filename or "")
    cf = await create_context_file(
        db,
        project_id=project_id,
        filename=file.filename or "unknown",
        file_size=len(content),
        content_type=file.content_type or "application/octet-stream",
        raw_content=raw_text,
    )
    await db.commit()
    # Trigger indexing (chunking + embedding)
    await index_context_file(db, cf)
    await db.commit()
    await db.refresh(cf)
    logger.info("context_file_uploaded", file_id=str(cf.id), project_id=str(project_id))
    return ContextFileDetailResponse(data=ContextFileResponse.model_validate(cf))


@router.get("", response_model=ContextFileListResponse)
async def list_context_files(
    project_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> ContextFileListResponse:
    """List all context files for a project."""
    role = await get_user_project_role(db, project_id, current_user.id)
    if role is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not a project member")
    files = await get_context_files_for_project(db, project_id)
    return ContextFileListResponse(
        data=[ContextFileResponse.model_validate(f) for f in files]
    )


@router.delete("/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_context_file(
    project_id: uuid.UUID,
    file_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> None:
    """Delete a context file from the project."""
    role = await get_user_project_role(db, project_id, current_user.id)
    if role is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not a project member")
    cf = await get_context_file_by_id(db, file_id)
    if cf is None or cf.project_id != project_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")
    await delete_context_file(db, cf)
    await db.commit()
    logger.info("context_file_deleted", file_id=str(file_id), project_id=str(project_id))


@router.post("/{file_id}/reindex", response_model=ContextFileDetailResponse)
async def reindex_file(
    project_id: uuid.UUID,
    file_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> ContextFileDetailResponse:
    """Re-index a context file: delete old chunks and regenerate embeddings."""
    role = await get_user_project_role(db, project_id, current_user.id)
    if role is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not a project member")
    cf = await get_context_file_by_id(db, file_id)
    if cf is None or cf.project_id != project_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")
    await reindex_context_file(db, cf)
    await db.commit()
    await db.refresh(cf)
    logger.info("context_file_reindexed", file_id=str(file_id))
    return ContextFileDetailResponse(data=ContextFileResponse.model_validate(cf))
