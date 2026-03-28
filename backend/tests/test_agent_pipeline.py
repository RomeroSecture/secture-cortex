"""Tests for the LangGraph multi-agent pipeline (Stories 7.1 + 7.4)."""

import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.schemas.agent import AgentInsight, PipelineState, SupervisorDecision
from app.services.agents.synthesizer import (
    _detect_conflicts,
    _generate_compound_insight,
    _is_duplicate,
    synthesizer_node,
)

# ─── Schema tests ───────────────────────────────────────────────


def test_agent_insight_to_legacy() -> None:
    """AgentInsight converts to legacy insight dict format."""
    insight = AgentInsight(
        agent_source="tech_lead",
        type="dependency_alert",
        subtype="dependency_alert",
        summary="Módulo X afecta Y",
        content="El cambio en X rompe la interfaz con Y.",
        confidence=0.85,
        sources=["architecture.md"],
        target_roles=["tech_lead", "developer"],
    )
    legacy = insight.to_legacy_insight()
    # Legacy type maps non-standard types to "suggestion"
    assert legacy["type"] == "suggestion"
    assert legacy["agent_source"] == "tech_lead"
    assert legacy["summary"] == "Módulo X afecta Y"
    assert legacy["confidence"] == 0.85


def test_agent_insight_to_legacy_standard_type() -> None:
    """Standard types (alert, scope, suggestion) pass through."""
    insight = AgentInsight(
        agent_source="pm",
        type="alert",
        summary="Alerta de scope",
        content="Fuera de scope.",
        confidence=0.9,
    )
    assert insight.to_legacy_insight()["type"] == "alert"


def test_agent_insight_to_ws_message() -> None:
    """WebSocket message format includes agent_source metadata."""
    insight = AgentInsight(
        agent_source="dev",
        type="code_reference",
        summary="Archivo relevante",
        content="Ver services/auth.py",
        confidence=0.7,
    )
    msg = insight.to_ws_message()
    assert msg["type"] == "role_insight"
    assert msg["payload"]["agent_source"] == "dev"
    assert msg["payload"]["type"] == "code_reference"


def test_supervisor_decision_validation() -> None:
    """SupervisorDecision validates agent names."""
    decision = SupervisorDecision(
        active_agents=["tech_lead", "pm"],
        reasoning="Technical and scope discussion",
        topic_classification="technical_scope",
    )
    assert decision.active_agents == ["tech_lead", "pm"]


def test_pipeline_state_structure() -> None:
    """PipelineState has all required keys."""
    state: PipelineState = {
        "transcription_chunk": "test",
        "context_chunks": [],
        "meeting_id": str(uuid.uuid4()),
        "project_id": str(uuid.uuid4()),
        "connected_roles": ["developer"],
        "active_agents": [],
        "agent_insights": [],
        "iteration_count": 0,
        "feedback_context": "",
        "previous_insights": [],
    }
    assert state["transcription_chunk"] == "test"


# ─── Synthesizer tests ─────────────────────────────────────────


def test_is_duplicate_exact_match() -> None:
    """Exact summary match is detected as duplicate."""
    insight = AgentInsight(
        agent_source="dev",
        type="suggestion",
        summary="Módulo auth necesita refactor",
        confidence=0.7,
    )
    previous = ["Módulo auth necesita refactor"]
    assert _is_duplicate(insight, previous) is True


def test_is_duplicate_case_insensitive() -> None:
    """Case-insensitive match works."""
    insight = AgentInsight(
        agent_source="dev",
        type="suggestion",
        summary="Test Summary",
        confidence=0.7,
    )
    assert _is_duplicate(insight, ["test summary"]) is True


def test_is_duplicate_no_match() -> None:
    """Different summary is not duplicate."""
    insight = AgentInsight(
        agent_source="dev",
        type="suggestion",
        summary="Nuevo insight",
        confidence=0.7,
    )
    assert _is_duplicate(insight, ["Otro insight"]) is False


def test_is_duplicate_empty_previous() -> None:
    """No previous → not duplicate."""
    insight = AgentInsight(
        agent_source="dev",
        type="suggestion",
        summary="Test",
        confidence=0.7,
    )
    assert _is_duplicate(insight, []) is False


@pytest.mark.asyncio
async def test_synthesizer_filters_low_confidence() -> None:
    """Insights below confidence threshold are filtered out."""
    state: PipelineState = {
        "transcription_chunk": "test",
        "context_chunks": ["some context"],
        "meeting_id": str(uuid.uuid4()),
        "project_id": str(uuid.uuid4()),
        "connected_roles": ["commercial"],
        "active_agents": ["commercial"],
        "agent_insights": [
            AgentInsight(
                agent_source="commercial",
                type="opportunity_detected",
                summary="Low confidence opportunity",
                confidence=0.3,
                target_roles=["commercial"],
            ),
            AgentInsight(
                agent_source="commercial",
                type="upsell_signal",
                summary="High confidence upsell",
                confidence=0.9,
                target_roles=["commercial"],
            ),
        ],
        "iteration_count": 0,
        "feedback_context": "",
        "previous_insights": [],
    }

    result = await synthesizer_node(state)
    filtered = result["agent_insights"]
    # 0.3 < 0.85 (commercial threshold) → filtered out
    # 0.9 >= 0.85 → passes
    assert len(filtered) == 1
    assert filtered[0].summary == "High confidence upsell"


@pytest.mark.asyncio
async def test_synthesizer_deduplicates() -> None:
    """Insights matching previous summaries are removed."""
    state: PipelineState = {
        "transcription_chunk": "test",
        "context_chunks": ["context"],
        "meeting_id": str(uuid.uuid4()),
        "project_id": str(uuid.uuid4()),
        "connected_roles": ["developer"],
        "active_agents": ["dev"],
        "agent_insights": [
            AgentInsight(
                agent_source="dev",
                type="suggestion",
                summary="Already seen insight",
                confidence=0.8,
                target_roles=["developer"],
            ),
            AgentInsight(
                agent_source="dev",
                type="code_reference",
                summary="New unique insight",
                confidence=0.8,
                target_roles=["developer"],
            ),
        ],
        "iteration_count": 0,
        "feedback_context": "",
        "previous_insights": ["Already seen insight"],
    }

    result = await synthesizer_node(state)
    filtered = result["agent_insights"]
    assert len(filtered) == 1
    assert filtered[0].summary == "New unique insight"


@pytest.mark.asyncio
async def test_synthesizer_empty_context_generates_hint() -> None:
    """When no context and no insights, generates insufficient_context hint."""
    state: PipelineState = {
        "transcription_chunk": "test",
        "context_chunks": [],
        "meeting_id": str(uuid.uuid4()),
        "project_id": str(uuid.uuid4()),
        "connected_roles": ["admin"],
        "active_agents": ["dev"],
        "agent_insights": [],
        "iteration_count": 0,
        "feedback_context": "",
        "previous_insights": [],
    }

    result = await synthesizer_node(state)
    filtered = result["agent_insights"]
    assert len(filtered) == 1
    assert filtered[0].subtype == "insufficient_context"
    assert filtered[0].agent_source == "supervisor"


@pytest.mark.asyncio
async def test_synthesizer_no_insights_returns_empty() -> None:
    """No insights + has context → returns empty (no hint)."""
    state: PipelineState = {
        "transcription_chunk": "test",
        "context_chunks": ["some context"],
        "meeting_id": str(uuid.uuid4()),
        "project_id": str(uuid.uuid4()),
        "connected_roles": [],
        "active_agents": [],
        "agent_insights": [],
        "iteration_count": 0,
        "feedback_context": "",
        "previous_insights": [],
    }

    result = await synthesizer_node(state)
    assert result["agent_insights"] == []


# ─── Supervisor tests ──────────────────────────────────────────


@pytest.mark.asyncio
async def test_supervisor_routes_technical_chunk() -> None:
    """Supervisor activates tech_lead for technical discussion."""
    mock_decision = SupervisorDecision(
        active_agents=["tech_lead", "dev"],
        reasoning="Technical topic about module dependencies",
        topic_classification="technical",
    )

    mock_model = MagicMock()
    mock_structured = AsyncMock(return_value=mock_decision)
    mock_model.with_structured_output.return_value = MagicMock(
        ainvoke=mock_structured,
    )

    with patch(
        "app.services.agents.supervisor._get_supervisor_model",
        return_value=mock_model,
    ):
        from app.services.agents.supervisor import supervisor_node

        state: PipelineState = {
            "transcription_chunk": "Necesitamos cambiar el módulo de auth",
            "context_chunks": ["auth module depends on JWT library"],
            "meeting_id": str(uuid.uuid4()),
            "project_id": str(uuid.uuid4()),
            "connected_roles": ["developer"],
            "active_agents": [],
            "agent_insights": [],
            "iteration_count": 0,
            "feedback_context": "",
            "previous_insights": [],
        }

        result = await supervisor_node(state)

    assert "tech_lead" in result["active_agents"]
    assert "dev" in result["active_agents"]


@pytest.mark.asyncio
async def test_supervisor_fallback_on_error() -> None:
    """Supervisor falls back to dev agent on LLM error."""
    with patch(
        "app.services.agents.supervisor._get_supervisor_model",
        side_effect=RuntimeError("LLM unavailable"),
    ):
        from app.services.agents.supervisor import supervisor_node

        state: PipelineState = {
            "transcription_chunk": "Hablemos del presupuesto",
            "context_chunks": [],
            "meeting_id": str(uuid.uuid4()),
            "project_id": str(uuid.uuid4()),
            "connected_roles": ["pm"],
            "active_agents": [],
            "agent_insights": [],
            "iteration_count": 0,
            "feedback_context": "",
            "previous_insights": [],
        }

        result = await supervisor_node(state)

    assert result["active_agents"] == ["dev"]


# ─── Pipeline build test ───────────────────────────────────────


def test_pipeline_builds_correctly() -> None:
    """StateGraph compiles without errors."""
    from app.services.agent_pipeline import build_pipeline

    graph = build_pipeline()
    compiled = graph.compile()
    assert compiled is not None


# ─── Agent node tests ──────────────────────────────────────────


@pytest.mark.asyncio
async def test_agent_node_graceful_failure() -> None:
    """Agent node returns empty insights on LLM failure."""
    with patch(
        "app.services.agents.tech_lead._get_specialist_model",
        side_effect=RuntimeError("Connection failed"),
    ):
        from app.services.agents.tech_lead import tech_lead_node

        state: PipelineState = {
            "transcription_chunk": "Test chunk",
            "context_chunks": [],
            "meeting_id": str(uuid.uuid4()),
            "project_id": str(uuid.uuid4()),
            "connected_roles": [],
            "active_agents": ["tech_lead"],
            "agent_insights": [],
            "iteration_count": 0,
            "feedback_context": "",
            "previous_insights": [],
        }

        result = await tech_lead_node(state)

    assert result["agent_insights"] == []


@pytest.mark.asyncio
async def test_agent_node_parses_valid_response() -> None:
    """Agent node parses LLM JSON response into AgentInsight list."""
    import json

    mock_final_msg = MagicMock()
    mock_final_msg.content = json.dumps({
        "insights": [
            {
                "type": "code_reference",
                "subtype": "code_reference",
                "summary": "Ver services/auth.py",
                "content": "El módulo auth está en services/auth.py.",
                "confidence": 0.75,
                "sources": ["project_structure.md"],
            }
        ]
    })
    mock_agent = AsyncMock()
    mock_agent.ainvoke = AsyncMock(
        return_value={"messages": [mock_final_msg]}
    )

    with patch(
        "app.services.agents.dev.create_react_agent",
        return_value=mock_agent,
    ):
        from app.services.agents.dev import dev_node

        state: PipelineState = {
            "transcription_chunk": "¿Dónde está el módulo de auth?",
            "context_chunks": ["auth module in services/auth.py"],
            "meeting_id": str(uuid.uuid4()),
            "project_id": str(uuid.uuid4()),
            "connected_roles": ["developer"],
            "active_agents": ["dev"],
            "agent_insights": [],
            "iteration_count": 0,
            "feedback_context": "",
            "previous_insights": [],
        }

        result = await dev_node(state)

    insights = result["agent_insights"]
    assert len(insights) == 1
    assert insights[0].agent_source == "dev"
    assert insights[0].type == "code_reference"
    assert insights[0].confidence == 0.75


# ─── Config tests ──────────────────────────────────────────────


def test_config_has_agent_pipeline_settings() -> None:
    """Config includes all agent pipeline settings."""
    from app.config import settings

    assert hasattr(settings, "agent_pipeline_enabled")
    assert hasattr(settings, "supervisor_model")
    assert hasattr(settings, "specialist_model")
    assert hasattr(settings, "confidence_tech_lead")
    assert hasattr(settings, "confidence_commercial")


# ─── Feature flag test ─────────────────────────────────────────


def test_rag_imports_agent_pipeline_conditionally() -> None:
    """RAG module imports agent_pipeline only when flag is enabled."""
    from app.services import rag

    assert hasattr(rag, "_run_agent_pipeline")
    assert hasattr(rag, "_run_legacy_pipeline")


# ─── Story 7.4: Conflict detection + role filtering ───────────


def test_detect_conflicts_finds_effort_vs_budget() -> None:
    """Detects conflict between effort_estimation and budget_impact."""
    insights = [
        AgentInsight(
            agent_source="tech_lead",
            type="alert",
            subtype="effort_estimation",
            summary="2 días fácil",
            confidence=0.8,
        ),
        AgentInsight(
            agent_source="pm",
            type="scope",
            subtype="budget_impact",
            summary="Desplaza Sprint 7 completo",
            confidence=0.85,
        ),
    ]
    conflicts = _detect_conflicts(insights)
    assert len(conflicts) == 1
    assert conflicts[0][0].agent_source != conflicts[0][1].agent_source


def test_detect_conflicts_ignores_same_agent() -> None:
    """No conflict when both insights are from the same agent."""
    insights = [
        AgentInsight(
            agent_source="tech_lead",
            type="alert",
            subtype="effort_estimation",
            summary="Insight A",
            confidence=0.8,
        ),
        AgentInsight(
            agent_source="tech_lead",
            type="alert",
            subtype="budget_impact",
            summary="Insight B",
            confidence=0.8,
        ),
    ]
    assert _detect_conflicts(insights) == []


def test_detect_conflicts_no_matching_types() -> None:
    """No conflict when types don't match conflict pairs."""
    insights = [
        AgentInsight(
            agent_source="tech_lead",
            type="alert",
            subtype="dependency_alert",
            summary="Dep A",
            confidence=0.8,
        ),
        AgentInsight(
            agent_source="dev",
            type="suggestion",
            subtype="code_reference",
            summary="Code B",
            confidence=0.7,
        ),
    ]
    assert _detect_conflicts(insights) == []


def test_generate_compound_insight() -> None:
    """Compound insight merges two conflicting perspectives."""
    a = AgentInsight(
        agent_source="tech_lead",
        type="alert",
        subtype="effort_estimation",
        summary="Cambio rápido",
        confidence=0.8,
        sources=["arch.md"],
        target_roles=["tech_lead", "developer"],
    )
    b = AgentInsight(
        agent_source="pm",
        type="scope",
        subtype="budget_impact",
        summary="Desplaza sprint",
        confidence=0.9,
        sources=["roadmap.md"],
        target_roles=["pm", "admin"],
    )
    compound = _generate_compound_insight(a, b)
    assert compound.agent_source == "supervisor"
    assert compound.subtype == "synthesis_conflict"
    assert "tech_lead" in compound.content
    assert "pm" in compound.content
    assert compound.confidence == 0.9  # max of both
    assert "tech_lead" in compound.target_roles
    assert "pm" in compound.target_roles


@pytest.mark.asyncio
async def test_synthesizer_generates_compound_on_conflict() -> None:
    """Synthesizer adds compound insight when conflict detected."""
    state: PipelineState = {
        "transcription_chunk": "test",
        "context_chunks": ["context"],
        "meeting_id": str(uuid.uuid4()),
        "project_id": str(uuid.uuid4()),
        "connected_roles": ["tech_lead", "pm"],
        "active_agents": ["tech_lead", "pm"],
        "agent_insights": [
            AgentInsight(
                agent_source="tech_lead",
                type="alert",
                subtype="effort_estimation",
                summary="Solo 2 días",
                confidence=0.8,
                target_roles=["tech_lead", "developer"],
            ),
            AgentInsight(
                agent_source="pm",
                type="scope",
                subtype="budget_impact",
                summary="Fuera de presupuesto",
                confidence=0.85,
                target_roles=["pm", "admin"],
            ),
        ],
        "iteration_count": 0,
        "feedback_context": "",
        "previous_insights": [],
    }

    result = await synthesizer_node(state)
    filtered = result["agent_insights"]
    # Should have original 2 + 1 compound = 3
    subtypes = [i.subtype for i in filtered]
    assert "synthesis_conflict" in subtypes
    assert len(filtered) == 3


# ─── MeetingManager role-filtered tests ────────────────────────


def test_role_connection_threshold() -> None:
    """RoleConnection gets threshold from settings."""
    from app.services.meeting_manager import RoleConnection

    mock_ws = MagicMock()
    conn = RoleConnection.create(mock_ws, "commercial")
    # Commercial threshold defaults to 0.85
    assert conn.confidence_threshold == 0.85
    assert conn.user_role == "commercial"


def test_meeting_manager_get_connected_roles() -> None:
    """get_connected_roles returns unique roles."""
    from app.services.meeting_manager import MeetingManager, RoleConnection

    mgr = MeetingManager()
    mid = uuid.uuid4()
    mgr.active_connections[mid] = [
        RoleConnection(ws=MagicMock(), user_role="pm"),
        RoleConnection(ws=MagicMock(), user_role="developer"),
        RoleConnection(ws=MagicMock(), user_role="pm"),
    ]
    roles = mgr.get_connected_roles(mid)
    assert set(roles) == {"pm", "developer"}
