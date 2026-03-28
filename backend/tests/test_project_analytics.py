"""Tests for project-level analytics and multi-meeting intelligence (Story 7.8)."""

import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.api.v1.project_analytics import (
    FreshnessItem,
    HealthScoreResponse,
    KBReport,
    KnowledgeGap,
    ProjectAnalyticsResponse,
)

# ─── Schema tests ──────────────────────────────────────────────


def test_health_score_response() -> None:
    """HealthScoreResponse validates correctly."""
    health = HealthScoreResponse(
        score=72.5,
        trend="improving",
        factors={
            "frequency": 30,
            "sentiment": 20,
            "engagement": 12.5,
            "recency": 10,
        },
    )
    assert health.score == 72.5
    assert health.trend == "improving"


def test_freshness_item() -> None:
    """FreshnessItem validates correctly."""
    item = FreshnessItem(
        file_id=str(uuid.uuid4()),
        filename="architecture.md",
        age_days=15,
        status="green",
        last_updated="2026-03-15T10:00:00Z",
    )
    assert item.status == "green"
    assert item.age_days == 15


def test_knowledge_gap() -> None:
    """KnowledgeGap validates correctly."""
    gap = KnowledgeGap(
        type="no_context_files",
        message="No hay archivos de contexto indexados.",
        severity="critical",
    )
    assert gap.severity == "critical"


def test_kb_report() -> None:
    """KBReport validates correctly."""
    report = KBReport(
        total_chunks=150,
        file_chunks=80,
        meeting_chunks=70,
        total_files=5,
        total_meetings=3,
        coverage_ratio=1.14,
    )
    assert report.total_chunks == 150
    assert report.coverage_ratio == 1.14


def test_full_analytics_response() -> None:
    """ProjectAnalyticsResponse validates full structure."""
    resp = ProjectAnalyticsResponse(
        health=HealthScoreResponse(
            score=65.0,
            trend="stable",
            factors={"frequency": 15, "sentiment": 20},
        ),
        freshness=[
            FreshnessItem(
                file_id=str(uuid.uuid4()),
                filename="test.md",
                age_days=5,
                status="green",
                last_updated="2026-03-23T10:00:00Z",
            ),
        ],
        gaps=[
            KnowledgeGap(
                type="coverage_imbalance",
                message="More meeting chunks than file chunks",
                severity="warning",
            ),
        ],
        kb_report=KBReport(
            total_chunks=100,
            file_chunks=30,
            meeting_chunks=70,
            total_files=2,
            total_meetings=5,
            coverage_ratio=0.43,
        ),
    )
    assert len(resp.freshness) == 1
    assert len(resp.gaps) == 1
    assert resp.kb_report.total_meetings == 5


# ─── Service logic tests ──────────────────────────────────────


@pytest.mark.asyncio
async def test_compute_kb_report_empty_project() -> None:
    """KB report for project with no data returns zeros."""
    from app.services.project_analytics import compute_kb_report

    mock_db = AsyncMock()
    # 4 queries: file_chunks, meeting_chunks, total_files, total_meetings
    mock_result = MagicMock()
    mock_result.scalar.return_value = 0
    mock_db.execute = AsyncMock(return_value=mock_result)

    report = await compute_kb_report(mock_db, uuid.uuid4())
    assert report["total_chunks"] == 0
    assert report["file_chunks"] == 0
    assert report["coverage_ratio"] == 0.0


@pytest.mark.asyncio
async def test_detect_gaps_no_files_with_meetings() -> None:
    """Detects critical gap when no files but meetings exist."""
    from app.services.project_analytics import detect_knowledge_gaps

    mock_db = AsyncMock()
    call_count = 0

    mock_result_0 = MagicMock()
    mock_result_0.scalar.return_value = 0
    mock_result_50 = MagicMock()
    mock_result_50.scalar.return_value = 50

    async def mock_execute(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        return mock_result_0 if call_count == 1 else mock_result_50

    mock_db.execute = mock_execute

    gaps = await detect_knowledge_gaps(mock_db, uuid.uuid4())
    assert any(g["type"] == "no_context_files" for g in gaps)
    assert any(g["severity"] == "critical" for g in gaps)


@pytest.mark.asyncio
async def test_health_score_no_meetings() -> None:
    """Health score returns 50 (neutral) for projects with no meetings."""
    from app.services.project_analytics import compute_relationship_health

    mock_db = AsyncMock()
    mock_result = MagicMock()
    mock_result.one.return_value = (0, None)
    mock_db.execute = AsyncMock(return_value=mock_result)

    health = await compute_relationship_health(mock_db, uuid.uuid4())
    assert health["score"] == 50.0
    assert health["trend"] == "stable"


# ─── Model test ────────────────────────────────────────────────


def test_client_profile_model() -> None:
    """ClientProfile model has expected attributes."""
    from app.models.client_profile import ClientProfile

    assert hasattr(ClientProfile, "project_id")
    assert hasattr(ClientProfile, "behavior_data")
    assert hasattr(ClientProfile, "health_score")
    assert hasattr(ClientProfile, "health_trend")
