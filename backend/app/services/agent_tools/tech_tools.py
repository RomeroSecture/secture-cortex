"""Tool implementations for the Tech Lead specialist agent.

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


def create_tech_tools(project_id: uuid.UUID) -> list:
    """Create Tech Lead tools bound to a project."""

    @tool
    async def search_dependencies(module_name: str) -> str:
        """Search project context for files and modules that depend on
        or are depended by the given module_name. Returns a list of
        related components and their relationships."""
        chunks = await search_context_by_query(
            project_id,
            f"dependencies imports requires {module_name}",
            top_k=5,
        )
        if not chunks:
            return f"No dependency info found for '{module_name}'."
        return (
            f"Dependencies related to '{module_name}':\n"
            + "\n---\n".join(chunks)
        )

    @tool
    async def check_architecture(topic: str) -> str:
        """Search architecture docs and project context for principles,
        patterns, and constraints related to the given topic. Use this
        to detect if a discussed change conflicts with architecture."""
        chunks = await search_context_by_query(
            project_id,
            f"architecture principle pattern constraint {topic}",
            top_k=5,
        )
        if not chunks:
            return f"No architecture info found for '{topic}'."
        return (
            f"Architecture context for '{topic}':\n"
            + "\n---\n".join(chunks)
        )

    @tool
    async def estimate_effort(description: str) -> str:
        """Produce a rough effort estimate for a described change based
        on the complexity visible in the project context. Returns an
        estimate in days with a complexity range."""
        chunks = await search_context_by_query(
            project_id,
            f"complexity implementation scope {description}",
            top_k=5,
        )
        context = "\n---\n".join(chunks) if chunks else "No context."
        return (
            f"Context for effort estimation of '{description}':\n"
            f"{context}\n\n"
            "Based on this context, provide your estimate in the "
            "insight (days range + complexity: low/medium/high)."
        )

    @tool
    async def recall_decisions(topic: str) -> str:
        """Search past meeting transcriptions for decisions related to
        the given topic. Returns relevant excerpts from previous
        meetings stored in pgvector."""
        chunks = await search_meeting_transcriptions(
            project_id,
            f"decision agreed decided {topic}",
            top_k=5,
        )
        if not chunks:
            return f"No past decisions found about '{topic}'."
        return (
            f"Past decisions related to '{topic}':\n"
            + "\n---\n".join(chunks)
        )

    @tool
    async def suggest_alternative(conflict_description: str) -> str:
        """Given a described conflict or problem, search the project
        context for alternative approaches, patterns, or solutions
        that have been documented or discussed."""
        chunks = await search_context_by_query(
            project_id,
            f"alternative approach solution pattern {conflict_description}",
            top_k=5,
        )
        if not chunks:
            return "No alternatives found in project context."
        return (
            "Relevant context for alternatives:\n"
            + "\n---\n".join(chunks)
        )

    @tool
    async def check_technical_debt(module_name: str) -> str:
        """Search project context for TODO, FIXME, HACK, tech-debt
        markers, and known issues related to the given module."""
        keyword_chunks = await search_context_by_keyword(
            project_id,
            module_name,
            top_k=10,
        )
        debt_markers = [
            c for c in keyword_chunks
            if any(
                m in c.upper()
                for m in ["TODO", "FIXME", "HACK", "DEBT", "WORKAROUND"]
            )
        ]
        if not debt_markers:
            semantic = await search_context_by_query(
                project_id,
                f"technical debt issue problem {module_name}",
                top_k=3,
            )
            if not semantic:
                return f"No tech debt found for '{module_name}'."
            return (
                f"Potential issues near '{module_name}':\n"
                + "\n---\n".join(semantic)
            )
        return (
            f"Tech debt markers for '{module_name}':\n"
            + "\n---\n".join(debt_markers)
        )

    return [
        search_dependencies,
        check_architecture,
        estimate_effort,
        recall_decisions,
        suggest_alternative,
        check_technical_debt,
    ]
