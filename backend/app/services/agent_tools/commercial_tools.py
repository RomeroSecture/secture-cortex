"""Tool implementations for the Commercial specialist agent.

All tools search the project's pgvector-indexed context. They do NOT
call external APIs — they query the indexed project knowledge base.
Tools are created via factory bound to a specific project_id.
"""

import uuid

from langchain_core.tools import tool

from app.services.agent_tools.vector_search import (
    search_context_by_keyword,
    search_context_by_query,
    search_meeting_transcriptions,
)


def create_commercial_tools(project_id: uuid.UUID) -> list:
    """Create Commercial agent tools bound to a project."""

    @tool
    async def search_services_catalog(pain_point: str) -> str:
        """Match a client pain point against Secture's service
        offerings indexed in the project context. Returns matching
        services, capabilities, and relevant case studies."""
        chunks = await search_context_by_query(
            project_id,
            (
                f"service offering capability solution "
                f"cybersecurity cloud data development {pain_point}"
            ),
            top_k=5,
        )
        if not chunks:
            return (
                f"No service match for '{pain_point}'. "
                "Secture offers: cybersecurity, data, cloud, dev."
            )
        return (
            f"Services matching '{pain_point}':\n"
            + "\n---\n".join(chunks)
        )

    @tool
    async def detect_opportunity(conversation_excerpt: str) -> str:
        """Analyze a conversation excerpt for business opportunity
        signals by searching project context for unmet needs,
        expansion areas, and growth indicators."""
        chunks = await search_context_by_query(
            project_id,
            (
                f"opportunity growth expansion need gap "
                f"improvement {conversation_excerpt}"
            ),
            top_k=5,
        )
        if not chunks:
            return "No opportunity signals found in project context."
        return (
            "Opportunity context:\n"
            + "\n---\n".join(chunks)
        )

    @tool
    async def check_competitive_position(competitor: str) -> str:
        """Search project context for information about competitors,
        alternative technologies, or market positioning that can
        help counter a competitor mention."""
        chunks = await search_context_by_query(
            project_id,
            f"competitor alternative comparison {competitor}",
            top_k=5,
        )
        keyword_hits = await search_context_by_keyword(
            project_id,
            competitor,
            top_k=5,
        )
        all_chunks = list(dict.fromkeys(chunks + keyword_hits))
        if not all_chunks:
            return (
                f"No competitive intelligence for '{competitor}' "
                "in project context."
            )
        return (
            f"Competitive context for '{competitor}':\n"
            + "\n---\n".join(all_chunks[:7])
        )

    @tool
    async def analyze_sentiment(text: str) -> str:
        """Search past meeting transcriptions for similar discussion
        topics to compare sentiment evolution over time. Provides
        historical sentiment context for the current topic."""
        chunks = await search_meeting_transcriptions(
            project_id,
            text,
            top_k=5,
        )
        if not chunks:
            return "No historical context for sentiment comparison."
        return (
            "Historical conversation context for sentiment:\n"
            + "\n---\n".join(chunks)
            + "\n\nCompare tone and sentiment with current text."
        )

    @tool
    async def check_contract_context() -> str:
        """Search project context for contract details, renewal
        dates, SLAs, and commercial terms that might be relevant
        to the current conversation."""
        chunks = await search_context_by_query(
            project_id,
            "contract renewal SLA terms commercial agreement deadline",
            top_k=5,
        )
        if not chunks:
            return "No contract details found in project context."
        return (
            "Contract context:\n"
            + "\n---\n".join(chunks)
        )

    return [
        search_services_catalog,
        detect_opportunity,
        check_competitive_position,
        analyze_sentiment,
        check_contract_context,
    ]
