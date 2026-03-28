"""Conversation events API — access detected patterns from meetings."""

import uuid
from typing import Annotated

import structlog
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.conversation_event import ConversationEvent
from app.models.meeting import Meeting
from app.models.user import User
from app.repositories.project import get_user_project_role

logger = structlog.get_logger()

router = APIRouter(
    prefix="/projects/{project_id}/meetings/{meeting_id}/events",
    tags=["conversation-events"],
)


class ConversationEventResponse(BaseModel):
    """API response for a conversation event."""

    id: uuid.UUID
    meeting_id: uuid.UUID
    type: str
    content: dict
    resolved: bool
    detected_at: str

    model_config = ConfigDict(from_attributes=True)


class ConversationEventListResponse(BaseModel):
    """Wrapped list of conversation events."""

    data: list[ConversationEventResponse]


@router.get("", response_model=ConversationEventListResponse)
async def list_conversation_events(
    project_id: uuid.UUID,
    meeting_id: uuid.UUID,
    event_type: str | None = None,
    db: Annotated[AsyncSession, Depends(get_db)] = None,
    current_user: Annotated[User, Depends(get_current_user)] = None,
) -> ConversationEventListResponse:
    """List conversation events for a meeting, optionally filtered by type."""
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

    query = (
        select(ConversationEvent)
        .where(ConversationEvent.meeting_id == meeting_id)
        .order_by(ConversationEvent.detected_at)
    )
    if event_type:
        query = query.where(ConversationEvent.type == event_type)

    result = await db.execute(query)
    events = result.scalars().all()

    return ConversationEventListResponse(
        data=[
            ConversationEventResponse(
                id=e.id,
                meeting_id=e.meeting_id,
                type=e.type,
                content=e.content,
                resolved=e.resolved,
                detected_at=str(e.detected_at),
            )
            for e in events
        ]
    )
