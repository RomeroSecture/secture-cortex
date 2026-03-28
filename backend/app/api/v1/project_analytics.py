"""Project-level analytics API — cross-meeting intelligence and KB health."""

import uuid
from typing import Annotated

import structlog
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.repositories.project import get_user_project_role
from app.services.project_analytics import (
    compute_context_freshness,
    compute_kb_report,
    compute_relationship_health,
    detect_knowledge_gaps,
)

logger = structlog.get_logger()

router = APIRouter(
    prefix="/projects/{project_id}/analytics",
    tags=["project-analytics"],
)


class HealthScoreResponse(BaseModel):
    """Relationship health score."""

    score: float
    trend: str
    factors: dict


class FreshnessItem(BaseModel):
    """Context file freshness indicator."""

    file_id: str
    filename: str
    age_days: int
    status: str
    last_updated: str


class KnowledgeGap(BaseModel):
    """Detected knowledge gap."""

    type: str
    message: str
    severity: str


class KBReport(BaseModel):
    """Knowledge base evolution report."""

    total_chunks: int
    file_chunks: int
    meeting_chunks: int
    total_files: int
    total_meetings: int
    coverage_ratio: float


class ProjectAnalyticsResponse(BaseModel):
    """Full project analytics response."""

    health: HealthScoreResponse
    freshness: list[FreshnessItem] = Field(default_factory=list)
    gaps: list[KnowledgeGap] = Field(default_factory=list)
    kb_report: KBReport


@router.get("", response_model=ProjectAnalyticsResponse)
async def get_project_analytics(
    project_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> ProjectAnalyticsResponse:
    """Get full project analytics: health, freshness, gaps, KB report."""
    role = await get_user_project_role(db, project_id, current_user.id)
    if role is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a project member",
        )

    health_data = await compute_relationship_health(db, project_id)
    freshness_data = await compute_context_freshness(db, project_id)
    gaps_data = await detect_knowledge_gaps(db, project_id)
    kb_data = await compute_kb_report(db, project_id)

    return ProjectAnalyticsResponse(
        health=HealthScoreResponse(**health_data),
        freshness=[FreshnessItem(**f) for f in freshness_data],
        gaps=[KnowledgeGap(**g) for g in gaps_data],
        kb_report=KBReport(**kb_data),
    )


@router.get("/health", response_model=HealthScoreResponse)
async def get_health_score(
    project_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> HealthScoreResponse:
    """Get relationship health score for the project."""
    role = await get_user_project_role(db, project_id, current_user.id)
    if role is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a project member",
        )

    data = await compute_relationship_health(db, project_id)
    return HealthScoreResponse(**data)
