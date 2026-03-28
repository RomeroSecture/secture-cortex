"""Meeting outputs API — access post-meeting generated artifacts."""

import uuid
from typing import Annotated

import structlog
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.meeting import Meeting
from app.models.meeting_output import MeetingOutput
from app.models.user import User
from app.repositories.project import get_user_project_role
from app.schemas.meeting_output import (
    MeetingOutputListResponse,
    MeetingOutputResponse,
)

logger = structlog.get_logger()

router = APIRouter(
    prefix="/projects/{project_id}/meetings/{meeting_id}/outputs",
    tags=["meeting-outputs"],
)


@router.get("", response_model=MeetingOutputListResponse)
async def list_meeting_outputs(
    project_id: uuid.UUID,
    meeting_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> MeetingOutputListResponse:
    """List all post-meeting outputs for a meeting."""
    role = await get_user_project_role(db, project_id, current_user.id)
    if role is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a project member",
        )

    meeting = await db.get(Meeting, meeting_id)
    if meeting is None or meeting.project_id != project_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meeting not found",
        )

    result = await db.execute(
        select(MeetingOutput)
        .where(MeetingOutput.meeting_id == meeting_id)
        .order_by(MeetingOutput.created_at)
    )
    outputs = result.scalars().all()

    return MeetingOutputListResponse(
        data=[MeetingOutputResponse.model_validate(o) for o in outputs]
    )


@router.get("/{output_type}", response_model=MeetingOutputResponse)
async def get_meeting_output_by_type(
    project_id: uuid.UUID,
    meeting_id: uuid.UUID,
    output_type: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> MeetingOutputResponse:
    """Get a specific post-meeting output by type."""
    role = await get_user_project_role(db, project_id, current_user.id)
    if role is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a project member",
        )

    result = await db.execute(
        select(MeetingOutput)
        .where(
            MeetingOutput.meeting_id == meeting_id,
            MeetingOutput.type == output_type,
        )
    )
    output = result.scalar_one_or_none()

    if output is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Output type '{output_type}' not found",
        )

    return MeetingOutputResponse.model_validate(output)
