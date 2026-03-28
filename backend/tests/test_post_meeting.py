"""Tests for post-meeting intelligence (Story 7.6)."""

import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.schemas.meeting_output import (
    BriefingOutput,
    EmailDraftOutput,
    HandoffOutput,
    MeetingOutputResponse,
    MinutesOutput,
    RetrospectiveOutput,
    SprintImpactOutput,
)

# ─── Schema tests ──────────────────────────────────────────────


def test_minutes_output_schema() -> None:
    """MinutesOutput has all required sections."""
    minutes = MinutesOutput(
        attendees=["Carlos", "Ana"],
        topics_covered=["Migración DB", "Sprint planning"],
        decisions=[{"what": "Usar PostgreSQL", "who": "Carlos"}],
        action_items=[{"task": "Crear PR", "owner": "Ana", "deadline": "lunes"}],
        summary="Reunión productiva sobre migración.",
    )
    assert len(minutes.attendees) == 2
    assert len(minutes.decisions) == 1


def test_handoff_output_schema() -> None:
    """HandoffOutput has all required fields."""
    handoff = HandoffOutput(
        topic_status=[{"topic": "auth", "status": "en progreso"}],
        pending_commitments=[{"who": "Ana", "what": "PR auth"}],
        open_questions=["¿Qué proveedor OAuth?"],
        context_for_next="Continuar con migración auth.",
    )
    assert len(handoff.open_questions) == 1


def test_email_draft_output_schema() -> None:
    """EmailDraftOutput has professional email structure."""
    email = EmailDraftOutput(
        subject="Resumen reunión 28/03",
        greeting="Estimado cliente,",
        body="En la reunión de hoy discutimos...",
        commitments=["Entrega auth el lunes"],
        next_steps=["Enviar propuesta ampliación"],
        closing="Saludos cordiales, Equipo Secture",
    )
    assert "Estimado" in email.greeting


def test_sprint_impact_output_schema() -> None:
    """SprintImpactOutput has impact assessment fields."""
    impact = SprintImpactOutput(
        total_requests=4,
        estimated_days=12.0,
        displaced_stories=["Story A", "Story B"],
        recommendation="Repriorizar sprint actual.",
    )
    assert impact.estimated_days == 12.0
    assert len(impact.displaced_stories) == 2


def test_briefing_output_schema() -> None:
    """BriefingOutput has internal briefing fields."""
    briefing = BriefingOutput(
        summary="Se decidió migrar la base de datos.",
        changes_for_team=["Nuevo ORM", "Tests actualizados"],
        key_decisions=["PostgreSQL over MongoDB"],
    )
    assert len(briefing.changes_for_team) == 2


def test_retrospective_output_schema() -> None:
    """RetrospectiveOutput has analytics fields."""
    retro = RetrospectiveOutput(
        duration_minutes=45,
        scope_ratio="3 in-scope, 1 out-of-scope",
        insights_generated=12,
        action_items_count=5,
    )
    assert retro.duration_minutes == 45


# ─── Output configs ───────────────────────────────────────────


def test_output_configs_has_6_types() -> None:
    """Post-meeting generates 6 different output types."""
    from app.services.agents.post_meeting import OUTPUT_CONFIGS

    assert len(OUTPUT_CONFIGS) == 6
    types = [cfg[0] for cfg in OUTPUT_CONFIGS]
    assert "minutes" in types
    assert "handoff" in types
    assert "sprint_impact" in types
    assert "email_draft" in types
    assert "briefing" in types
    assert "retrospective" in types


# ─── Service tests (mocked LLM) ───────────────────────────────


@pytest.mark.asyncio
async def test_generate_post_meeting_returns_outputs() -> None:
    """generate_post_meeting_outputs produces MeetingOutput records."""
    from app.services.agents.post_meeting import (
        generate_post_meeting_outputs,
    )

    meeting_id = uuid.uuid4()

    # Mock DB session
    mock_db = AsyncMock()

    # Mock transcription query
    mock_segments_result = MagicMock()
    mock_segments_result.scalars.return_value.all.return_value = []

    # Mock insights query
    mock_insights_result = MagicMock()
    mock_insights_result.scalars.return_value.all.return_value = []

    mock_db.execute = AsyncMock(
        side_effect=[mock_segments_result, mock_insights_result]
    )
    mock_db.add = MagicMock()
    mock_db.commit = AsyncMock()

    # Mock all LLM calls to return valid JSON
    import json

    mock_response = MagicMock()
    mock_response.content = json.dumps({
        "summary": "Test meeting",
        "attendees": ["Speaker 0"],
    })

    mock_model = AsyncMock()
    mock_model.ainvoke = AsyncMock(return_value=mock_response)

    with patch(
        "app.services.agents.post_meeting._get_model",
        return_value=mock_model,
    ):
        outputs = await generate_post_meeting_outputs(
            mock_db, meeting_id
        )

    # Should produce 6 outputs (one per config)
    assert len(outputs) == 6
    assert mock_db.add.call_count == 6
    assert mock_db.commit.call_count == 1


@pytest.mark.asyncio
async def test_generate_post_meeting_handles_partial_failure() -> None:
    """If some outputs fail, others still get generated."""
    from app.services.agents.post_meeting import (
        generate_post_meeting_outputs,
    )

    meeting_id = uuid.uuid4()
    mock_db = AsyncMock()

    mock_segments_result = MagicMock()
    mock_segments_result.scalars.return_value.all.return_value = []
    mock_insights_result = MagicMock()
    mock_insights_result.scalars.return_value.all.return_value = []
    mock_db.execute = AsyncMock(
        side_effect=[mock_segments_result, mock_insights_result]
    )
    mock_db.add = MagicMock()
    mock_db.commit = AsyncMock()

    import json

    call_count = 0

    async def mock_invoke(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        if call_count == 2:
            raise RuntimeError("LLM error on 2nd call")
        resp = MagicMock()
        resp.content = json.dumps({"summary": "ok"})
        return resp

    mock_model = MagicMock()
    mock_model.ainvoke = mock_invoke

    with patch(
        "app.services.agents.post_meeting._get_model",
        return_value=mock_model,
    ):
        outputs = await generate_post_meeting_outputs(
            mock_db, meeting_id
        )

    # 5 of 6 succeed (one failed)
    assert len(outputs) == 5


# ─── API endpoint test ─────────────────────────────────────────


def test_meeting_output_response_schema() -> None:
    """MeetingOutputResponse validates from dict."""
    data = {
        "id": str(uuid.uuid4()),
        "meeting_id": str(uuid.uuid4()),
        "type": "minutes",
        "content": {"summary": "Test"},
        "created_at": "2026-03-28T12:00:00Z",
    }
    resp = MeetingOutputResponse.model_validate(data)
    assert resp.type == "minutes"
    assert resp.content["summary"] == "Test"
