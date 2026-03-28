"""Tests for agent tools and tool-equipped agents (Stories 7.2 + 7.3)."""

import json
import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.schemas.agent import PipelineState

# ─── Tool factory tests ────────────────────────────────────────


def test_tech_tools_factory_creates_6_tools() -> None:
    """create_tech_tools returns exactly 6 tools."""
    from app.services.agent_tools.tech_tools import create_tech_tools

    tools = create_tech_tools(uuid.uuid4())
    assert len(tools) == 6
    names = {t.name for t in tools}
    assert "search_dependencies" in names
    assert "check_architecture" in names
    assert "estimate_effort" in names
    assert "recall_decisions" in names
    assert "suggest_alternative" in names
    assert "check_technical_debt" in names


def test_dev_tools_factory_creates_5_tools() -> None:
    """create_dev_tools returns exactly 5 tools."""
    from app.services.agent_tools.dev_tools import create_dev_tools

    tools = create_dev_tools(uuid.uuid4())
    assert len(tools) == 5
    names = {t.name for t in tools}
    assert "search_project_context" in names
    assert "find_code_reference" in names
    assert "suggest_pattern" in names
    assert "analyze_api_impact" in names
    assert "check_test_coverage" in names


def test_tools_have_docstrings() -> None:
    """All tools have non-empty descriptions for LLM tool calling."""
    from app.services.agent_tools.dev_tools import create_dev_tools
    from app.services.agent_tools.tech_tools import create_tech_tools

    pid = uuid.uuid4()
    for t in create_tech_tools(pid) + create_dev_tools(pid):
        assert t.description, f"Tool {t.name} has no description"
        assert len(t.description) > 20, (
            f"Tool {t.name} description too short"
        )


# ─── Tool execution tests (mocked pgvector) ───────────────────


@pytest.mark.asyncio
async def test_search_dependencies_returns_results() -> None:
    """search_dependencies returns formatted context results."""
    from app.services.agent_tools.tech_tools import create_tech_tools

    pid = uuid.uuid4()
    tools = create_tech_tools(pid)
    search_deps = next(t for t in tools if t.name == "search_dependencies")

    with patch(
        "app.services.agent_tools.tech_tools.search_context_by_query",
        new_callable=AsyncMock,
        return_value=["auth imports jwt_utils", "jwt_utils used by middleware"],
    ):
        result = await search_deps.ainvoke({"module_name": "auth"})

    assert "auth" in result
    assert "jwt_utils" in result


@pytest.mark.asyncio
async def test_search_dependencies_no_results() -> None:
    """search_dependencies returns 'not found' when no matches."""
    from app.services.agent_tools.tech_tools import create_tech_tools

    pid = uuid.uuid4()
    tools = create_tech_tools(pid)
    search_deps = next(t for t in tools if t.name == "search_dependencies")

    with patch(
        "app.services.agent_tools.tech_tools.search_context_by_query",
        new_callable=AsyncMock,
        return_value=[],
    ):
        result = await search_deps.ainvoke({"module_name": "nonexistent"})

    assert "No dependency info found" in result


@pytest.mark.asyncio
async def test_check_technical_debt_with_markers() -> None:
    """check_technical_debt finds TODO/FIXME markers."""
    from app.services.agent_tools.tech_tools import create_tech_tools

    pid = uuid.uuid4()
    tools = create_tech_tools(pid)
    debt_tool = next(t for t in tools if t.name == "check_technical_debt")

    with patch(
        "app.services.agent_tools.tech_tools.search_context_by_keyword",
        new_callable=AsyncMock,
        return_value=[
            "# TODO: refactor auth module to use OAuth2",
            "Auth module handles JWT validation",
        ],
    ):
        result = await debt_tool.ainvoke({"module_name": "auth"})

    assert "TODO" in result
    assert "auth" in result


@pytest.mark.asyncio
async def test_find_code_reference_combines_sources() -> None:
    """find_code_reference merges semantic and keyword results."""
    from app.services.agent_tools.dev_tools import create_dev_tools

    pid = uuid.uuid4()
    tools = create_dev_tools(pid)
    code_ref = next(t for t in tools if t.name == "find_code_reference")

    with (
        patch(
            "app.services.agent_tools.dev_tools.search_context_by_query",
            new_callable=AsyncMock,
            return_value=["services/auth.py handles authentication"],
        ),
        patch(
            "app.services.agent_tools.dev_tools.search_context_by_keyword",
            new_callable=AsyncMock,
            return_value=["auth module in services/auth.py, 150 LOC"],
        ),
    ):
        result = await code_ref.ainvoke({"module_name": "auth"})

    assert "auth" in result
    assert "services/auth.py" in result


@pytest.mark.asyncio
async def test_recall_decisions_searches_transcriptions() -> None:
    """recall_decisions queries past meeting transcriptions."""
    from app.services.agent_tools.tech_tools import create_tech_tools

    pid = uuid.uuid4()
    tools = create_tech_tools(pid)
    recall = next(t for t in tools if t.name == "recall_decisions")

    with patch(
        "app.services.agent_tools.tech_tools.search_meeting_transcriptions",
        new_callable=AsyncMock,
        return_value=["Decidimos usar PostgreSQL en vez de MongoDB"],
    ):
        result = await recall.ainvoke({"topic": "database"})

    assert "PostgreSQL" in result


# ─── Agent with tools tests (mocked LLM) ──────────────────────


@pytest.mark.asyncio
async def test_tech_lead_with_tools_parses_response() -> None:
    """Tech Lead agent parses insights from ReAct agent response."""
    from app.services.agents.tech_lead import (
        _parse_insights_from_response,
    )

    content = json.dumps({
        "insights": [{
            "type": "dependency_alert",
            "subtype": "dependency_alert",
            "summary": "Auth afecta middleware JWT",
            "content": "Cambiar auth impacta jwt_middleware.",
            "confidence": 0.85,
            "sources": ["architecture.md"],
        }]
    })
    result = _parse_insights_from_response(content)
    assert len(result) == 1
    assert result[0]["type"] == "dependency_alert"


@pytest.mark.asyncio
async def test_parse_insights_handles_wrapped_json() -> None:
    """Parser extracts JSON even with surrounding text."""
    from app.services.agents.tech_lead import (
        _parse_insights_from_response,
    )

    content = (
        'Here are my insights: {"insights": [{"type": "suggestion",'
        ' "summary": "test", "content": "test", "confidence": 0.7,'
        ' "sources": []}]} End.'
    )
    result = _parse_insights_from_response(content)
    assert len(result) == 1


@pytest.mark.asyncio
async def test_parse_insights_returns_empty_on_garbage() -> None:
    """Parser returns empty list on unparseable content."""
    from app.services.agents.tech_lead import (
        _parse_insights_from_response,
    )

    assert _parse_insights_from_response("not json at all") == []
    assert _parse_insights_from_response("") == []


@pytest.mark.asyncio
async def test_tech_lead_node_graceful_failure_with_tools() -> None:
    """Tech Lead node returns empty on create_react_agent failure."""
    with patch(
        "app.services.agents.tech_lead.create_react_agent",
        side_effect=RuntimeError("LLM down"),
    ):
        from app.services.agents.tech_lead import tech_lead_node

        state: PipelineState = {
            "transcription_chunk": "Cambiar módulo auth",
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
async def test_dev_node_graceful_failure_with_tools() -> None:
    """Dev node returns empty on failure."""
    with patch(
        "app.services.agents.dev.create_react_agent",
        side_effect=RuntimeError("LLM down"),
    ):
        from app.services.agents.dev import dev_node

        state: PipelineState = {
            "transcription_chunk": "¿Dónde está el servicio de pagos?",
            "context_chunks": [],
            "meeting_id": str(uuid.uuid4()),
            "project_id": str(uuid.uuid4()),
            "connected_roles": [],
            "active_agents": ["dev"],
            "agent_insights": [],
            "iteration_count": 0,
            "feedback_context": "",
            "previous_insights": [],
        }
        result = await dev_node(state)

    assert result["agent_insights"] == []


@pytest.mark.asyncio
async def test_tech_lead_full_invocation_mocked() -> None:
    """Tech Lead node invokes ReAct agent and parses result."""
    mock_final_msg = MagicMock()
    mock_final_msg.content = json.dumps({
        "insights": [{
            "type": "effort_estimation",
            "subtype": "effort_estimation",
            "summary": "Cambio en auth: 2-3 días",
            "content": "Complejidad media. Requiere actualizar tests.",
            "confidence": 0.75,
            "sources": ["auth_module.md"],
        }]
    })
    mock_agent = AsyncMock()
    mock_agent.ainvoke = AsyncMock(
        return_value={"messages": [mock_final_msg]}
    )

    with patch(
        "app.services.agents.tech_lead.create_react_agent",
        return_value=mock_agent,
    ):
        from app.services.agents.tech_lead import tech_lead_node

        state: PipelineState = {
            "transcription_chunk": "Necesitamos cambiar el auth",
            "context_chunks": ["auth uses JWT with bcrypt"],
            "meeting_id": str(uuid.uuid4()),
            "project_id": str(uuid.uuid4()),
            "connected_roles": ["tech_lead"],
            "active_agents": ["tech_lead"],
            "agent_insights": [],
            "iteration_count": 0,
            "feedback_context": "",
            "previous_insights": [],
        }
        result = await tech_lead_node(state)

    insights = result["agent_insights"]
    assert len(insights) == 1
    assert insights[0].agent_source == "tech_lead"
    assert insights[0].type == "effort_estimation"
    assert insights[0].confidence == 0.75


@pytest.mark.asyncio
async def test_dev_full_invocation_mocked() -> None:
    """Dev node invokes ReAct agent and parses result."""
    mock_final_msg = MagicMock()
    mock_final_msg.content = json.dumps({
        "insights": [{
            "type": "code_reference",
            "subtype": "code_reference",
            "summary": "Servicio de pagos en services/payments.py",
            "content": "El módulo de pagos está en services/payments.py.",
            "confidence": 0.8,
            "sources": ["project_structure.md"],
        }]
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
            "transcription_chunk": "¿Dónde está el servicio de pagos?",
            "context_chunks": ["payments module handles Stripe"],
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


# ─── Story 7.3: PM + Commercial tool factories ────────────────


def test_pm_tools_factory_creates_6_tools() -> None:
    """create_pm_tools returns exactly 6 tools."""
    from app.services.agent_tools.pm_tools import create_pm_tools

    tools = create_pm_tools(uuid.uuid4())
    assert len(tools) == 6
    names = {t.name for t in tools}
    assert "classify_scope" in names
    assert "track_budget_impact" in names
    assert "check_roadmap" in names
    assert "detect_risk" in names
    assert "track_commitment" in names
    assert "check_scope_ceiling" in names


def test_commercial_tools_factory_creates_5_tools() -> None:
    """create_commercial_tools returns exactly 5 tools."""
    from app.services.agent_tools.commercial_tools import (
        create_commercial_tools,
    )

    tools = create_commercial_tools(uuid.uuid4())
    assert len(tools) == 5
    names = {t.name for t in tools}
    assert "search_services_catalog" in names
    assert "detect_opportunity" in names
    assert "check_competitive_position" in names
    assert "analyze_sentiment" in names
    assert "check_contract_context" in names


def test_pm_commercial_tools_have_docstrings() -> None:
    """All PM/Commercial tools have descriptions for LLM."""
    from app.services.agent_tools.commercial_tools import (
        create_commercial_tools,
    )
    from app.services.agent_tools.pm_tools import create_pm_tools

    pid = uuid.uuid4()
    for t in create_pm_tools(pid) + create_commercial_tools(pid):
        assert t.description, f"Tool {t.name} missing description"


# ─── PM tool execution tests ──────────────────────────────────


@pytest.mark.asyncio
async def test_classify_scope_returns_context() -> None:
    """classify_scope returns scope context for classification."""
    from app.services.agent_tools.pm_tools import create_pm_tools

    tools = create_pm_tools(uuid.uuid4())
    scope_tool = next(t for t in tools if t.name == "classify_scope")

    with patch(
        "app.services.agent_tools.pm_tools.search_context_by_query",
        new_callable=AsyncMock,
        return_value=["Feature X planned for Q3 sprint"],
    ):
        result = await scope_tool.ainvoke({"request": "Feature X"})

    assert "Feature X" in result
    assert "planned" in result.lower() or "Q3" in result


@pytest.mark.asyncio
async def test_detect_risk_searches_keyword_and_semantic() -> None:
    """detect_risk combines semantic and keyword searches."""
    from app.services.agent_tools.pm_tools import create_pm_tools

    tools = create_pm_tools(uuid.uuid4())
    risk_tool = next(t for t in tools if t.name == "detect_risk")

    with (
        patch(
            "app.services.agent_tools.pm_tools.search_context_by_query",
            new_callable=AsyncMock,
            return_value=["Risk: auth migration may break SSO"],
        ),
        patch(
            "app.services.agent_tools.pm_tools.search_context_by_keyword",
            new_callable=AsyncMock,
            return_value=["Risk register: auth module HIGH priority"],
        ),
    ):
        result = await risk_tool.ainvoke({"topic": "auth migration"})

    assert "auth" in result.lower()


# ─── Commercial tool execution tests ──────────────────────────


@pytest.mark.asyncio
async def test_search_services_catalog_matches() -> None:
    """search_services_catalog finds matching services."""
    from app.services.agent_tools.commercial_tools import (
        create_commercial_tools,
    )

    tools = create_commercial_tools(uuid.uuid4())
    catalog = next(
        t for t in tools if t.name == "search_services_catalog"
    )

    with patch(
        "app.services.agent_tools.commercial_tools.search_context_by_query",
        new_callable=AsyncMock,
        return_value=["Secture cybersecurity: pentesting, audits"],
    ):
        result = await catalog.ainvoke({"pain_point": "security audit"})

    assert "cybersecurity" in result.lower()


@pytest.mark.asyncio
async def test_check_contract_context_no_results() -> None:
    """check_contract_context returns fallback when no data."""
    from app.services.agent_tools.commercial_tools import (
        create_commercial_tools,
    )

    tools = create_commercial_tools(uuid.uuid4())
    contract = next(
        t for t in tools if t.name == "check_contract_context"
    )

    with patch(
        "app.services.agent_tools.commercial_tools.search_context_by_query",
        new_callable=AsyncMock,
        return_value=[],
    ):
        result = await contract.ainvoke({})

    assert "No contract details" in result


# ─── PM/Commercial agent node tests ───────────────────────────


@pytest.mark.asyncio
async def test_pm_node_full_invocation() -> None:
    """PM node invokes ReAct agent and parses result."""
    mock_final_msg = MagicMock()
    mock_final_msg.content = json.dumps({
        "insights": [{
            "type": "scope_classification",
            "subtype": "scope_classification",
            "summary": "Feature X: fuera de scope, esfuerzo alto",
            "content": "No está en el roadmap actual. ~5 días.",
            "confidence": 0.85,
            "sources": ["roadmap.md"],
        }]
    })
    mock_agent = AsyncMock()
    mock_agent.ainvoke = AsyncMock(
        return_value={"messages": [mock_final_msg]}
    )

    with patch(
        "app.services.agents.pm.create_react_agent",
        return_value=mock_agent,
    ):
        from app.services.agents.pm import pm_node

        state: PipelineState = {
            "transcription_chunk": "El cliente pide Feature X",
            "context_chunks": ["roadmap: Q3 features are A, B, C"],
            "meeting_id": str(uuid.uuid4()),
            "project_id": str(uuid.uuid4()),
            "connected_roles": ["pm"],
            "active_agents": ["pm"],
            "agent_insights": [],
            "iteration_count": 0,
            "feedback_context": "",
            "previous_insights": [],
        }
        result = await pm_node(state)

    insights = result["agent_insights"]
    assert len(insights) == 1
    assert insights[0].agent_source == "pm"
    assert insights[0].type == "scope_classification"
    assert "pm" in insights[0].target_roles


@pytest.mark.asyncio
async def test_commercial_node_full_invocation() -> None:
    """Commercial node invokes ReAct agent and parses result."""
    mock_final_msg = MagicMock()
    mock_final_msg.content = json.dumps({
        "insights": [{
            "type": "opportunity_detected",
            "subtype": "opportunity_detected",
            "summary": "Cliente menciona problemas de seguridad",
            "content": "Secture ofrece pentesting y auditorías.",
            "confidence": 0.9,
            "sources": ["services_catalog.md"],
        }]
    })
    mock_agent = AsyncMock()
    mock_agent.ainvoke = AsyncMock(
        return_value={"messages": [mock_final_msg]}
    )

    with patch(
        "app.services.agents.commercial.create_react_agent",
        return_value=mock_agent,
    ):
        from app.services.agents.commercial import commercial_node

        state: PipelineState = {
            "transcription_chunk": "Tenemos problemas de seguridad",
            "context_chunks": ["Secture: cybersecurity services"],
            "meeting_id": str(uuid.uuid4()),
            "project_id": str(uuid.uuid4()),
            "connected_roles": ["commercial"],
            "active_agents": ["commercial"],
            "agent_insights": [],
            "iteration_count": 0,
            "feedback_context": "",
            "previous_insights": [],
        }
        result = await commercial_node(state)

    insights = result["agent_insights"]
    assert len(insights) == 1
    assert insights[0].agent_source == "commercial"
    assert insights[0].type == "opportunity_detected"
    assert "commercial" in insights[0].target_roles


@pytest.mark.asyncio
async def test_pm_node_graceful_failure() -> None:
    """PM node returns empty on failure."""
    with patch(
        "app.services.agents.pm.create_react_agent",
        side_effect=RuntimeError("LLM down"),
    ):
        from app.services.agents.pm import pm_node

        state: PipelineState = {
            "transcription_chunk": "test",
            "context_chunks": [],
            "meeting_id": str(uuid.uuid4()),
            "project_id": str(uuid.uuid4()),
            "connected_roles": [],
            "active_agents": ["pm"],
            "agent_insights": [],
            "iteration_count": 0,
            "feedback_context": "",
            "previous_insights": [],
        }
        result = await pm_node(state)

    assert result["agent_insights"] == []


@pytest.mark.asyncio
async def test_commercial_node_graceful_failure() -> None:
    """Commercial node returns empty on failure."""
    with patch(
        "app.services.agents.commercial.create_react_agent",
        side_effect=RuntimeError("LLM down"),
    ):
        from app.services.agents.commercial import commercial_node

        state: PipelineState = {
            "transcription_chunk": "test",
            "context_chunks": [],
            "meeting_id": str(uuid.uuid4()),
            "project_id": str(uuid.uuid4()),
            "connected_roles": [],
            "active_agents": ["commercial"],
            "agent_insights": [],
            "iteration_count": 0,
            "feedback_context": "",
            "previous_insights": [],
        }
        result = await commercial_node(state)

    assert result["agent_insights"] == []
