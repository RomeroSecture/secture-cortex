"""Meeting management endpoints: start, end, list, get."""

import uuid
from typing import Annotated

import structlog
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.insight import Insight
from app.models.meeting import MeetingStatus
from app.models.transcription import Transcription
from app.models.user import User
from app.repositories.meeting import (
    create_meeting,
    end_meeting,
    get_meeting_by_id,
    get_meetings_for_project,
)
from app.repositories.project import get_user_project_role
from app.schemas.meeting import (
    MeetingCreate,
    MeetingDetailResponse,
    MeetingListResponse,
    MeetingResponse,
    MeetingUpdate,
)
from app.schemas.transcription import (
    MeetingDetailFullResponse,
    TranscriptionSegmentResponse,
)

logger = structlog.get_logger()

router = APIRouter(prefix="/projects/{project_id}/meetings", tags=["meetings"])


@router.post("", response_model=MeetingDetailResponse, status_code=status.HTTP_201_CREATED)
async def start_meeting(
    project_id: uuid.UUID,
    payload: MeetingCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> MeetingDetailResponse:
    """Start a new meeting linked to a project."""
    role = await get_user_project_role(db, project_id, current_user.id)
    if role is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not a project member")
    meeting = await create_meeting(db, project_id=project_id, title=payload.title)
    await db.commit()
    logger.info("meeting_started", meeting_id=str(meeting.id), project_id=str(project_id))
    return MeetingDetailResponse(data=MeetingResponse.model_validate(meeting))


@router.post("/{meeting_id}/end", response_model=MeetingDetailResponse)
async def stop_meeting(
    project_id: uuid.UUID,
    meeting_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> MeetingDetailResponse:
    """End an in-progress meeting."""
    role = await get_user_project_role(db, project_id, current_user.id)
    if role is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not a project member")
    meeting = await get_meeting_by_id(db, meeting_id)
    if meeting is None or meeting.project_id != project_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Meeting not found")
    if meeting.status != MeetingStatus.RECORDING:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Meeting is not recording"
        )
    meeting = await end_meeting(db, meeting)
    await db.commit()
    # Story 5.3: Embed transcription into pgvector for future RAG
    from app.services.meeting_indexer import index_meeting_transcription

    await index_meeting_transcription(db, meeting)
    await db.commit()

    # Story 7.6: Generate post-meeting intelligence (async, non-blocking)
    import asyncio

    asyncio.create_task(
        _generate_outputs_background(meeting_id)
    )

    logger.info("meeting_ended", meeting_id=str(meeting_id))
    return MeetingDetailResponse(data=MeetingResponse.model_validate(meeting))


@router.patch("/{meeting_id}", response_model=MeetingDetailResponse)
async def rename_meeting(
    project_id: uuid.UUID,
    meeting_id: uuid.UUID,
    payload: MeetingUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> MeetingDetailResponse:
    """Rename a meeting."""
    role = await get_user_project_role(db, project_id, current_user.id)
    if role is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not a project member")
    meeting = await get_meeting_by_id(db, meeting_id)
    if meeting is None or meeting.project_id != project_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Meeting not found")
    meeting.title = payload.title
    await db.commit()
    await db.refresh(meeting)
    return MeetingDetailResponse(data=MeetingResponse.model_validate(meeting))


@router.get("", response_model=MeetingListResponse)
async def list_meetings(
    project_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> MeetingListResponse:
    """List all meetings for a project."""
    role = await get_user_project_role(db, project_id, current_user.id)
    if role is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not a project member")
    meetings = await get_meetings_for_project(db, project_id)
    return MeetingListResponse(data=[MeetingResponse.model_validate(m) for m in meetings])


@router.get("/{meeting_id}", response_model=MeetingDetailResponse)
async def get_meeting(
    project_id: uuid.UUID,
    meeting_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> MeetingDetailResponse:
    """Get a single meeting by ID."""
    role = await get_user_project_role(db, project_id, current_user.id)
    if role is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not a project member")
    meeting = await get_meeting_by_id(db, meeting_id)
    if meeting is None or meeting.project_id != project_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Meeting not found")
    return MeetingDetailResponse(data=MeetingResponse.model_validate(meeting))


@router.get("/{meeting_id}/full", response_model=MeetingDetailFullResponse)
async def get_meeting_full(
    project_id: uuid.UUID,
    meeting_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> MeetingDetailFullResponse:
    """Get full meeting detail with transcription and insight count."""
    role = await get_user_project_role(db, project_id, current_user.id)
    if role is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not a project member")
    meeting = await get_meeting_by_id(db, meeting_id)
    if meeting is None or meeting.project_id != project_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Meeting not found")
    result = await db.execute(
        select(Transcription)
        .where(Transcription.meeting_id == meeting_id)
        .order_by(Transcription.timestamp)
    )
    segments = list(result.scalars().all())
    result = await db.execute(
        select(func.count()).where(Insight.meeting_id == meeting_id)
    )
    insight_count = result.scalar() or 0
    return MeetingDetailFullResponse(
        meeting_id=meeting.id,
        title=meeting.title,
        status=meeting.status.value,
        started_at=meeting.started_at,
        ended_at=meeting.ended_at,
        transcription=[TranscriptionSegmentResponse.model_validate(s) for s in segments],
        insight_count=insight_count,
    )


async def _generate_outputs_background(meeting_id: uuid.UUID) -> None:
    """Generate post-meeting outputs in background (non-blocking)."""
    from app.database import async_session
    from app.services.agents.post_meeting import generate_post_meeting_outputs

    try:
        async with async_session() as db:
            await generate_post_meeting_outputs(db, meeting_id)
    except Exception:
        logger.exception(
            "post_meeting_background_failed",
            meeting_id=str(meeting_id),
        )
