"""Project-level analytics — cross-meeting trends, health score, KB health.

Computes intelligence that spans multiple meetings for a project.
"""

import uuid
from datetime import UTC, datetime, timedelta

import structlog
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.client_profile import ClientProfile
from app.models.context_chunk import ContextChunk
from app.models.context_file import ContextFile
from app.models.insight import Insight
from app.models.meeting import Meeting, MeetingStatus
from app.models.sentiment_point import SentimentPoint

logger = structlog.get_logger()


async def compute_relationship_health(
    db: AsyncSession,
    project_id: uuid.UUID,
) -> dict:
    """Compute a 0-100 relationship health score for the project.

    Factors: meeting frequency, sentiment trend, resolution rate,
    outstanding commitments.
    """
    # Meeting count and recency
    result = await db.execute(
        select(func.count(), func.max(Meeting.ended_at))
        .where(
            Meeting.project_id == project_id,
            Meeting.status == MeetingStatus.ENDED,
        )
    )
    row = result.one()
    meeting_count = row[0] or 0
    last_meeting = row[1]

    if meeting_count == 0:
        return {
            "score": 50.0,
            "trend": "stable",
            "factors": {"meetings": 0},
        }

    # Frequency score: meetings in last 30 days
    thirty_days_ago = datetime.now(UTC) - timedelta(days=30)
    result = await db.execute(
        select(func.count())
        .where(
            Meeting.project_id == project_id,
            Meeting.status == MeetingStatus.ENDED,
            Meeting.ended_at >= thirty_days_ago,
        )
    )
    recent_meetings = result.scalar() or 0
    frequency_score = min(recent_meetings * 15, 30)  # max 30 pts

    # Sentiment score: average across all meetings
    result = await db.execute(
        select(func.avg(SentimentPoint.score))
        .join(Meeting, Meeting.id == SentimentPoint.meeting_id)
        .where(Meeting.project_id == project_id)
    )
    avg_sentiment = result.scalar() or 0.0
    sentiment_score = max(0, min(30, (avg_sentiment + 1) * 15))

    # Insight engagement score (how many insights generated)
    result = await db.execute(
        select(func.count())
        .select_from(Insight)
        .join(Meeting, Meeting.id == Insight.meeting_id)
        .where(Meeting.project_id == project_id)
    )
    total_insights = result.scalar() or 0
    engagement_score = min(total_insights * 2, 20)  # max 20 pts

    # Recency bonus
    recency_score = 0
    if last_meeting:
        days_since = (datetime.now(UTC) - last_meeting).days
        recency_score = max(0, 20 - days_since)  # max 20 pts

    total = frequency_score + sentiment_score + engagement_score + recency_score
    health = min(100.0, max(0.0, total))

    # Determine trend
    trend = "stable"
    if recent_meetings >= 2 and avg_sentiment > 0.2:
        trend = "improving"
    elif recent_meetings == 0 or avg_sentiment < -0.2:
        trend = "declining"

    return {
        "score": round(health, 1),
        "trend": trend,
        "factors": {
            "frequency": round(frequency_score, 1),
            "sentiment": round(sentiment_score, 1),
            "engagement": round(engagement_score, 1),
            "recency": round(recency_score, 1),
            "meetings_total": meeting_count,
            "meetings_recent": recent_meetings,
        },
    }


async def compute_context_freshness(
    db: AsyncSession,
    project_id: uuid.UUID,
) -> list[dict]:
    """Compute freshness indicators for context files.

    Green: updated in last 30 days
    Yellow: 30-90 days old
    Red: >90 days old
    """
    result = await db.execute(
        select(ContextFile)
        .where(ContextFile.project_id == project_id)
        .order_by(ContextFile.updated_at.desc())
    )
    files = result.scalars().all()
    now = datetime.now(UTC)

    freshness = []
    for f in files:
        age_days = (now - f.updated_at).days
        if age_days <= 30:
            status = "green"
        elif age_days <= 90:
            status = "yellow"
        else:
            status = "red"

        freshness.append({
            "file_id": str(f.id),
            "filename": f.filename,
            "age_days": age_days,
            "status": status,
            "last_updated": f.updated_at.isoformat(),
        })

    return freshness


async def detect_knowledge_gaps(
    db: AsyncSession,
    project_id: uuid.UUID,
) -> list[dict]:
    """Detect topics discussed in meetings but not covered by context.

    Compares meeting transcription topics against context file topics
    using chunk counts as a proxy for coverage.
    """
    # Count context chunks from files vs meetings
    result = await db.execute(
        select(func.count())
        .where(
            ContextChunk.project_id == project_id,
            ContextChunk.context_file_id.is_not(None),
        )
    )
    file_chunks = result.scalar() or 0

    result = await db.execute(
        select(func.count())
        .where(
            ContextChunk.project_id == project_id,
            ContextChunk.context_file_id.is_(None),
        )
    )
    meeting_chunks = result.scalar() or 0

    gaps = []
    if meeting_chunks > file_chunks * 2:
        gaps.append({
            "type": "coverage_imbalance",
            "message": (
                f"Hay {meeting_chunks} chunks de reuniones vs "
                f"{file_chunks} de archivos. Subir más documentación."
            ),
            "severity": "warning",
        })

    if file_chunks == 0 and meeting_chunks > 0:
        gaps.append({
            "type": "no_context_files",
            "message": (
                "No hay archivos de contexto indexados. "
                "Las reuniones generan insights sin contexto de proyecto."
            ),
            "severity": "critical",
        })

    return gaps


async def compute_kb_report(
    db: AsyncSession,
    project_id: uuid.UUID,
) -> dict:
    """Generate a knowledge base evolution report."""
    # Total chunks by source
    result = await db.execute(
        select(func.count())
        .where(
            ContextChunk.project_id == project_id,
            ContextChunk.context_file_id.is_not(None),
        )
    )
    file_chunks = result.scalar() or 0

    result = await db.execute(
        select(func.count())
        .where(
            ContextChunk.project_id == project_id,
            ContextChunk.context_file_id.is_(None),
        )
    )
    meeting_chunks = result.scalar() or 0

    # Total files
    result = await db.execute(
        select(func.count())
        .where(ContextFile.project_id == project_id)
    )
    total_files = result.scalar() or 0

    # Total meetings
    result = await db.execute(
        select(func.count())
        .where(Meeting.project_id == project_id)
    )
    total_meetings = result.scalar() or 0

    return {
        "total_chunks": file_chunks + meeting_chunks,
        "file_chunks": file_chunks,
        "meeting_chunks": meeting_chunks,
        "total_files": total_files,
        "total_meetings": total_meetings,
        "coverage_ratio": (
            round(file_chunks / max(meeting_chunks, 1), 2)
        ),
    }


async def update_client_profile(
    db: AsyncSession,
    project_id: uuid.UUID,
) -> ClientProfile:
    """Update or create the client behavior profile for a project."""
    health = await compute_relationship_health(db, project_id)

    result = await db.execute(
        select(ClientProfile)
        .where(ClientProfile.project_id == project_id)
    )
    profile = result.scalar_one_or_none()

    if profile is None:
        profile = ClientProfile(
            project_id=project_id,
            behavior_data={},
            health_score=health["score"],
            health_trend=health["trend"],
        )
        db.add(profile)
    else:
        profile.health_score = health["score"]
        profile.health_trend = health["trend"]

    await db.commit()
    await db.refresh(profile)
    return profile
