"""Tests for conversation intelligence node (Story 7.5)."""

import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.schemas.agent import PipelineState
from app.schemas.conversation import (
    ConversationIntelOutput,
    DetectedActionItem,
    DetectedDecision,
    DetectedQuestion,
    SentimentDetection,
)
from app.services.agents.conversation import (
    _intel_to_insights,
    conversation_intel_node,
)

# ─── Schema tests ──────────────────────────────────────────────


def test_conversation_intel_output_defaults() -> None:
    """ConversationIntelOutput has sane defaults when nothing detected."""
    output = ConversationIntelOutput()
    assert output.decision is None
    assert output.action_item is None
    assert output.question is None
    assert output.topic_label == "general"
    assert output.sentiment is None


def test_conversation_intel_output_full() -> None:
    """ConversationIntelOutput populates all fields."""
    output = ConversationIntelOutput(
        decision=DetectedDecision(
            description="Usar PostgreSQL",
            speaker="Carlos",
        ),
        action_item=DetectedActionItem(
            task="Migrar DB",
            owner="Ana",
            deadline="viernes",
        ),
        question=DetectedQuestion(
            question="¿Cuánto cuesta?",
            speaker="Cliente",
        ),
        topic_label="base_de_datos",
        sentiment=SentimentDetection(
            topic="migración",
            sentiment="neutral",
            score=0.1,
        ),
        momentum_keyword="rendimiento",
        jargon_detected="ORM: herramienta que mapea tablas a objetos",
    )
    assert output.decision.speaker == "Carlos"
    assert output.action_item.deadline == "viernes"
    assert output.sentiment.score == 0.1


# ─── Intel-to-insights conversion ─────────────────────────────


def test_intel_to_insights_decision() -> None:
    """Decision detected → generates decision_detected insight."""
    intel = ConversationIntelOutput(
        decision=DetectedDecision(
            description="Migramos a PostgreSQL",
            speaker="Carlos",
            context="Discusión sobre base de datos",
        ),
    )
    insights = _intel_to_insights(intel)
    assert len(insights) == 1
    assert insights[0].subtype == "decision_detected"
    assert insights[0].agent_source == "conversation"
    assert "Carlos" in insights[0].content


def test_intel_to_insights_action_item() -> None:
    """Action item → generates action_item insight."""
    intel = ConversationIntelOutput(
        action_item=DetectedActionItem(
            task="Preparar propuesta técnica",
            owner="Ana",
            deadline="lunes",
        ),
    )
    insights = _intel_to_insights(intel)
    assert len(insights) == 1
    assert insights[0].subtype == "action_item"
    assert "Ana" in insights[0].content
    assert "lunes" in insights[0].content


def test_intel_to_insights_question() -> None:
    """Question → generates question_pending insight."""
    intel = ConversationIntelOutput(
        question=DetectedQuestion(
            question="¿Cuánto tiempo tardaría la migración?",
            speaker="Cliente",
        ),
    )
    insights = _intel_to_insights(intel)
    assert len(insights) == 1
    assert insights[0].subtype == "question_pending"
    assert "pm" in insights[0].target_roles


def test_intel_to_insights_jargon() -> None:
    """Jargon → generates jargon_translation for non-tech roles."""
    intel = ConversationIntelOutput(
        jargon_detected="API REST: interfaz para que sistemas se comuniquen",
    )
    insights = _intel_to_insights(intel)
    assert len(insights) == 1
    assert insights[0].subtype == "jargon_translation"
    assert "pm" in insights[0].target_roles
    assert "commercial" in insights[0].target_roles
    assert "developer" not in insights[0].target_roles


def test_intel_to_insights_momentum() -> None:
    """Momentum keyword → generates momentum_alert insight."""
    intel = ConversationIntelOutput(
        momentum_keyword="rendimiento",
    )
    insights = _intel_to_insights(intel)
    assert len(insights) == 1
    assert insights[0].subtype == "momentum_alert"
    assert "rendimiento" in insights[0].content


def test_intel_to_insights_multiple_detections() -> None:
    """Multiple detections → multiple insights."""
    intel = ConversationIntelOutput(
        decision=DetectedDecision(description="Usar React"),
        action_item=DetectedActionItem(task="Crear PR", owner="Dev"),
        jargon_detected="PR: solicitud de revisión de código",
    )
    insights = _intel_to_insights(intel)
    assert len(insights) == 3
    subtypes = {i.subtype for i in insights}
    assert "decision_detected" in subtypes
    assert "action_item" in subtypes
    assert "jargon_translation" in subtypes


def test_intel_to_insights_empty() -> None:
    """No detections → empty list."""
    intel = ConversationIntelOutput()
    assert _intel_to_insights(intel) == []


# ─── Node invocation tests ────────────────────────────────────


@pytest.mark.asyncio
async def test_conversation_node_invocation() -> None:
    """Conversation node invokes LLM and returns insights."""
    import json

    mock_response = MagicMock()
    mock_response.content = json.dumps({
        "decision": {
            "description": "Lanzar v2 en marzo",
            "speaker": "PM",
            "context": "",
        },
        "topic_label": "release",
        "sentiment": {
            "topic": "release",
            "sentiment": "positive",
            "score": 0.7,
        },
    })

    mock_model = AsyncMock()
    mock_model.ainvoke = AsyncMock(return_value=mock_response)

    with patch(
        "app.services.agents.conversation._get_conversation_model",
        return_value=mock_model,
    ):
        state: PipelineState = {
            "transcription_chunk": "OK, lanzamos v2 en marzo",
            "context_chunks": [],
            "meeting_id": str(uuid.uuid4()),
            "project_id": str(uuid.uuid4()),
            "connected_roles": ["pm"],
            "active_agents": [],
            "agent_insights": [],
            "iteration_count": 0,
            "feedback_context": "",
            "previous_insights": [],
            "final_insights": [],
        }
        result = await conversation_intel_node(state)

    insights = result["agent_insights"]
    assert len(insights) == 1
    assert insights[0].subtype == "decision_detected"


@pytest.mark.asyncio
async def test_conversation_node_graceful_failure() -> None:
    """Conversation node returns empty on LLM failure."""
    with patch(
        "app.services.agents.conversation._get_conversation_model",
        side_effect=RuntimeError("Model unavailable"),
    ):
        state: PipelineState = {
            "transcription_chunk": "test",
            "context_chunks": [],
            "meeting_id": str(uuid.uuid4()),
            "project_id": str(uuid.uuid4()),
            "connected_roles": [],
            "active_agents": [],
            "agent_insights": [],
            "iteration_count": 0,
            "feedback_context": "",
            "previous_insights": [],
            "final_insights": [],
        }
        result = await conversation_intel_node(state)

    assert result["agent_insights"] == []
