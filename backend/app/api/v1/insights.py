"""Insight listing and feedback endpoints."""

import uuid
from typing import Annotated

import structlog
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.insight import FeedbackRating, Insight, InsightFeedback
from app.models.user import User
from app.repositories.meeting import get_meeting_by_id
from app.repositories.project import get_user_project_role
from app.schemas.insight import (
    FeedbackCreate,
    FeedbackDetailResponse,
    FeedbackResponse,
    InsightListResponse,
    InsightResponse,
)

logger = structlog.get_logger()

router = APIRouter(tags=["insights"])


@router.get(
    "/projects/{project_id}/meetings/{meeting_id}/insights",
    response_model=InsightListResponse,
)
async def list_insights(
    project_id: uuid.UUID,
    meeting_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> InsightListResponse:
    """List all insights for a meeting."""
    role = await get_user_project_role(db, project_id, current_user.id)
    if role is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a project member",
        )
    # Verify meeting belongs to this project (prevent cross-project data leak)
    meeting = await get_meeting_by_id(db, meeting_id)
    if meeting is None or meeting.project_id != project_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meeting not found",
        )
    result = await db.execute(
        select(Insight)
        .where(Insight.meeting_id == meeting_id)
        .order_by(Insight.created_at.desc())
    )
    insights = list(result.scalars().all())
    return InsightListResponse(
        data=[InsightResponse.model_validate(i) for i in insights]
    )


@router.post(
    "/insights/{insight_id}/feedback",
    response_model=FeedbackDetailResponse,
    status_code=status.HTTP_201_CREATED,
)
async def submit_feedback(
    insight_id: uuid.UUID,
    payload: FeedbackCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> FeedbackDetailResponse:
    """Submit feedback (useful/not_useful/dismissed) on an insight."""
    result = await db.execute(
        select(Insight).where(Insight.id == insight_id)
    )
    insight = result.scalar_one_or_none()
    if insight is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Insight not found",
        )
    feedback = InsightFeedback(
        insight_id=insight_id,
        user_id=current_user.id,
        rating=FeedbackRating(payload.rating),
    )
    db.add(feedback)
    await db.commit()
    logger.info(
        "insight_feedback",
        insight_id=str(insight_id),
        rating=payload.rating,
    )
    return FeedbackDetailResponse(
        data=FeedbackResponse(insight_id=insight_id, rating=payload.rating)
    )
