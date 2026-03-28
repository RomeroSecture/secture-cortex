"""Meeting analytics API — KPIs, sentiment, auto-proposals, ticket drafts."""

import uuid
from typing import Annotated

import structlog
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.conversation_event import ConversationEvent
from app.models.insight import Insight
from app.models.meeting import Meeting
from app.models.sentiment_point import SentimentPoint
from app.models.transcription import Transcription
from app.models.user import User
from app.repositories.project import get_user_project_role

logger = structlog.get_logger()

router = APIRouter(
    prefix="/projects/{project_id}/meetings/{meeting_id}/analytics",
    tags=["analytics"],
)


class MeetingKPIs(BaseModel):
    """Real-time meeting KPIs."""

    total_insights: int = 0
    insights_by_type: dict[str, int] = Field(default_factory=dict)
    total_transcription_segments: int = 0
    total_decisions: int = 0
    total_action_items: int = 0
    total_questions_pending: int = 0
    total_commitments: int = 0
    speaker_counts: dict[str, int] = Field(default_factory=dict)


class MeetingKPIsResponse(BaseModel):
    """Wrapped KPIs response."""

    data: MeetingKPIs


class SentimentPointResponse(BaseModel):
    """A single sentiment data point."""

    topic: str | None
    sentiment: str
    score: float
    timestamp: str


class SentimentTimelineResponse(BaseModel):
    """Sentiment timeline for a meeting."""

    data: list[SentimentPointResponse]


@router.get("/kpis", response_model=MeetingKPIsResponse)
async def get_meeting_kpis(
    project_id: uuid.UUID,
    meeting_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> MeetingKPIsResponse:
    """Get real-time KPIs for a meeting."""
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

    # Insights by type
    result = await db.execute(
        select(Insight.type, func.count())
        .where(Insight.meeting_id == meeting_id)
        .group_by(Insight.type)
    )
    type_counts = {row[0].value: row[1] for row in result.all()}
    total_insights = sum(type_counts.values())

    # Transcription segments + speaker counts
    result = await db.execute(
        select(Transcription.speaker, func.count())
        .where(Transcription.meeting_id == meeting_id)
        .group_by(Transcription.speaker)
    )
    speaker_counts = {row[0]: row[1] for row in result.all()}
    total_segments = sum(speaker_counts.values())

    # Conversation events by type
    result = await db.execute(
        select(ConversationEvent.type, func.count())
        .where(ConversationEvent.meeting_id == meeting_id)
        .group_by(ConversationEvent.type)
    )
    event_counts = {row[0]: row[1] for row in result.all()}

    return MeetingKPIsResponse(data=MeetingKPIs(
        total_insights=total_insights,
        insights_by_type=type_counts,
        total_transcription_segments=total_segments,
        total_decisions=event_counts.get("decision", 0),
        total_action_items=event_counts.get("action_item", 0),
        total_questions_pending=event_counts.get("question", 0),
        total_commitments=event_counts.get("commitment", 0),
        speaker_counts=speaker_counts,
    ))


@router.get("/sentiment", response_model=SentimentTimelineResponse)
async def get_sentiment_timeline(
    project_id: uuid.UUID,
    meeting_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> SentimentTimelineResponse:
    """Get sentiment timeline for a meeting."""
    role = await get_user_project_role(db, project_id, current_user.id)
    if role is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a project member",
        )

    result = await db.execute(
        select(SentimentPoint)
        .where(SentimentPoint.meeting_id == meeting_id)
        .order_by(SentimentPoint.timestamp)
    )
    points = result.scalars().all()

    return SentimentTimelineResponse(
        data=[
            SentimentPointResponse(
                topic=p.topic,
                sentiment=p.sentiment,
                score=p.score,
                timestamp=str(p.timestamp),
            )
            for p in points
        ]
    )
