"""Database operations for Meeting model."""

import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.meeting import Meeting, MeetingStatus


async def create_meeting(
    db: AsyncSession, *, project_id: uuid.UUID, title: str
) -> Meeting:
    """Create a new meeting in recording state."""
    meeting = Meeting(
        project_id=project_id,
        title=title,
        status=MeetingStatus.RECORDING,
        started_at=datetime.now(UTC),
    )
    db.add(meeting)
    await db.flush()
    await db.refresh(meeting)
    return meeting


async def get_meeting_by_id(db: AsyncSession, meeting_id: uuid.UUID) -> Meeting | None:
    """Get a meeting by ID."""
    result = await db.execute(select(Meeting).where(Meeting.id == meeting_id))
    return result.scalar_one_or_none()


async def get_meetings_for_project(
    db: AsyncSession, project_id: uuid.UUID
) -> list[Meeting]:
    """Get all meetings for a project, ordered by start time descending."""
    result = await db.execute(
        select(Meeting)
        .where(Meeting.project_id == project_id)
        .order_by(Meeting.started_at.desc())
    )
    return list(result.scalars().all())


async def end_meeting(db: AsyncSession, meeting: Meeting) -> Meeting:
    """End a meeting: set status to ended and record end time."""
    meeting.status = MeetingStatus.ENDED
    meeting.ended_at = datetime.now(UTC)
    await db.flush()
    await db.refresh(meeting)
    return meeting
