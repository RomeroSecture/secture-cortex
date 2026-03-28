"""Tool implementations for the PM specialist agent.

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


def create_pm_tools(project_id: uuid.UUID) -> list:
    """Create PM agent tools bound to a project."""

    @tool
    async def classify_scope(request: str) -> str:
        """Classify a client request by searching the project context
        for scope definitions, planned features, and backlog items.
        Returns context to determine: in-scope, planned, or
        out-of-scope, with effort level (low/medium/high)."""
        chunks = await search_context_by_query(
            project_id,
            f"scope roadmap backlog planned feature {request}",
            top_k=5,
        )
        if not chunks:
            return (
                f"No scope context found for '{request}'. "
                "Likely out-of-scope — confirm with project docs."
            )
        return (
            f"Scope context for '{request}':\n"
            + "\n---\n".join(chunks)
            + "\n\nClassify as: in-scope | planned | out-of-scope "
            "× low | medium | high effort."
        )

    @tool
    async def track_budget_impact(requests_summary: str) -> str:
        """Search project context for budget, sprint capacity, and
        resource allocation info to evaluate the accumulated impact
        of meeting requests. Provide a summary of all requests
        classified so far in this meeting."""
        chunks = await search_context_by_query(
            project_id,
            "budget sprint capacity resources days available",
            top_k=5,
        )
        if not chunks:
            return (
                "No budget/capacity context found. "
                "Estimate based on typical sprint capacity."
            )
        return (
            "Budget/capacity context:\n"
            + "\n---\n".join(chunks)
            + f"\n\nRequests to evaluate: {requests_summary}"
        )

    @tool
    async def check_roadmap(request: str) -> str:
        """Compare a client request against the planned roadmap by
        searching for milestones, sprints, and prioritized work."""
        chunks = await search_context_by_query(
            project_id,
            f"roadmap milestone sprint priority plan {request}",
            top_k=5,
        )
        if not chunks:
            return f"No roadmap items found related to '{request}'."
        return (
            f"Roadmap context for '{request}':\n"
            + "\n---\n".join(chunks)
        )

    @tool
    async def detect_risk(topic: str) -> str:
        """Search the project's risk register and context for
        documented risks, mitigations, and concerns about a topic."""
        chunks = await search_context_by_query(
            project_id,
            f"risk concern blocker mitigation issue {topic}",
            top_k=5,
        )
        keyword_hits = await search_context_by_keyword(
            project_id,
            "risk",
            top_k=5,
        )
        all_chunks = list(dict.fromkeys(chunks + keyword_hits))
        if not all_chunks:
            return f"No documented risks found for '{topic}'."
        return (
            f"Risk context for '{topic}':\n"
            + "\n---\n".join(all_chunks[:7])
        )

    @tool
    async def track_commitment(
        statement: str,
        speaker: str,
    ) -> str:
        """Search past meeting transcriptions for previous
        commitments by the same speaker or about the same topic,
        to detect commitment collisions or patterns."""
        chunks = await search_meeting_transcriptions(
            project_id,
            f"commitment promise deliver deadline {speaker} {statement}",
            top_k=5,
        )
        if not chunks:
            return (
                f"No prior commitments found for {speaker} "
                f"about '{statement}'."
            )
        return (
            f"Prior commitments context for {speaker}:\n"
            + "\n---\n".join(chunks)
        )

    @tool
    async def check_scope_ceiling() -> str:
        """Search project context for configured scope ceilings,
        budget limits, and sprint boundaries to compare against
        accumulated effort in the current meeting."""
        chunks = await search_context_by_query(
            project_id,
            "scope ceiling budget limit maximum capacity threshold",
            top_k=5,
        )
        if not chunks:
            return (
                "No scope ceiling configured. "
                "Default: use sprint capacity as ceiling."
            )
        return (
            "Scope ceiling context:\n"
            + "\n---\n".join(chunks)
        )

    return [
        classify_scope,
        track_budget_impact,
        check_roadmap,
        detect_risk,
        track_commitment,
        check_scope_ceiling,
    ]
