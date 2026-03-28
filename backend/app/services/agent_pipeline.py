"""LangGraph StateGraph multi-agent pipeline — replaces monolithic RAG when enabled.

Architecture: START → supervisor → [parallel agents] → synthesizer → END
Uses AsyncPostgresSaver for meeting-level state persistence with graceful fallback.
"""

import asyncio
import uuid

import structlog
from langgraph.graph import END, START, StateGraph

from app.config import settings
from app.schemas.agent import AgentInsight, PipelineState
from app.services.agents.commercial import commercial_node
from app.services.agents.conversation import conversation_intel_node
from app.services.agents.dev import dev_node
from app.services.agents.pm import pm_node
from app.services.agents.supervisor import supervisor_node
from app.services.agents.synthesizer import synthesizer_node
from app.services.agents.tech_lead import tech_lead_node

logger = structlog.get_logger()

# Agent node registry — maps name to async function
AGENT_NODES: dict[str, object] = {
    "tech_lead": tech_lead_node,
    "pm": pm_node,
    "commercial": commercial_node,
    "dev": dev_node,
}


async def _parallel_agents_node(state: PipelineState) -> dict:
    """Fan-out to activated agents, run in parallel, merge results.

    This node runs all activated agents concurrently using asyncio.gather.
    Each agent returns {"agent_insights": [...]}, and results are merged.
    If an agent fails, others continue (graceful degradation — NFR21).
    """
    active = state.get("active_agents", [])

    tasks = []
    agent_names = []
    for name in active:
        node_fn = AGENT_NODES.get(name)
        if node_fn:
            tasks.append(node_fn(state))
            agent_names.append(name)

    # Conversation intelligence ALWAYS runs alongside specialists
    tasks.append(conversation_intel_node(state))
    agent_names.append("conversation_intel")

    # Run all concurrently — return_exceptions=True for graceful degradation
    results = await asyncio.gather(*tasks, return_exceptions=True)

    all_insights: list[AgentInsight] = []
    for name, result in zip(agent_names, results, strict=False):
        if isinstance(result, Exception):
            logger.error("agent_failed", agent=name, error=str(result))
            continue
        insights = result.get("agent_insights", [])
        all_insights.extend(insights)

    logger.info(
        "parallel_agents_done",
        active=agent_names,
        total_insights=len(all_insights),
    )
    return {"agent_insights": all_insights}


def build_pipeline() -> StateGraph:
    """Build the LangGraph StateGraph for the multi-agent pipeline.

    Graph topology:
      START → supervisor → parallel_agents → synthesizer → END

    The supervisor decides which agents to activate, parallel_agents runs them
    concurrently, and synthesizer merges/filters the results.
    """
    graph = StateGraph(PipelineState)

    # Nodes
    graph.add_node("supervisor", supervisor_node)
    graph.add_node("parallel_agents", _parallel_agents_node)
    graph.add_node("synthesizer", synthesizer_node)

    # Edges
    graph.add_edge(START, "supervisor")
    graph.add_edge("supervisor", "parallel_agents")
    graph.add_edge("parallel_agents", "synthesizer")
    graph.add_edge("synthesizer", END)

    return graph


# Compiled pipeline (lazy singleton)
_compiled_pipeline = None
_checkpointer = None


async def _get_checkpointer():
    """Get AsyncPostgresSaver instance, or None if unavailable."""
    global _checkpointer
    if _checkpointer is not None:
        return _checkpointer

    try:
        from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

        # Derive psycopg connection string from asyncpg one
        db_url = settings.database_url.replace("+asyncpg", "")
        _checkpointer = AsyncPostgresSaver.from_conn_string(db_url)
        await _checkpointer.setup()
        logger.info("checkpointer_initialized", backend="AsyncPostgresSaver")
        return _checkpointer
    except Exception:
        logger.warning("checkpointer_unavailable_running_stateless")
        return None


async def get_pipeline():
    """Get the compiled pipeline with optional checkpointer."""
    global _compiled_pipeline
    if _compiled_pipeline is not None:
        return _compiled_pipeline

    graph = build_pipeline()
    checkpointer = await _get_checkpointer()
    _compiled_pipeline = graph.compile(checkpointer=checkpointer)
    logger.info("pipeline_compiled", has_checkpointer=checkpointer is not None)
    return _compiled_pipeline


async def run_pipeline(
    transcription_chunk: str,
    context_chunks: list[str],
    meeting_id: uuid.UUID,
    project_id: uuid.UUID,
    connected_roles: list[str] | None = None,
    feedback_context: str = "",
    previous_insights: list[str] | None = None,
) -> list[AgentInsight]:
    """Run the multi-agent pipeline on a transcription chunk.

    Returns a list of filtered AgentInsight objects ready for delivery.
    """
    pipeline = await get_pipeline()

    initial_state: PipelineState = {
        "transcription_chunk": transcription_chunk,
        "context_chunks": context_chunks,
        "meeting_id": str(meeting_id),
        "project_id": str(project_id),
        "connected_roles": connected_roles or [],
        "active_agents": [],
        "agent_insights": [],
        "iteration_count": 0,
        "feedback_context": feedback_context,
        "previous_insights": previous_insights or [],
    }

    # Use meeting_id as thread_id for state isolation per meeting
    config = {"configurable": {"thread_id": str(meeting_id)}}

    try:
        result = await pipeline.ainvoke(initial_state, config=config)
        insights = result.get("agent_insights", [])
        logger.info(
            "pipeline_completed",
            meeting_id=str(meeting_id),
            insights_count=len(insights),
        )
        return insights
    except Exception:
        logger.exception("pipeline_failed")
        return []
