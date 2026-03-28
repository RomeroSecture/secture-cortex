"""Tool implementations for the Dev specialist agent.

All tools search the project's pgvector-indexed context. They do NOT
call external APIs — they query the indexed project knowledge base.
Tools are created via factory bound to a specific project_id.
"""

import uuid

from langchain_core.tools import tool

from app.services.agent_tools.vector_search import (
    search_context_by_keyword,
    search_context_by_query,
)


def create_dev_tools(project_id: uuid.UUID) -> list:
    """Create Dev agent tools bound to a project."""

    @tool
    async def search_project_context(topic: str) -> str:
        """Broad context search for background information about a
        topic. Use this when the conversation references something
        the team might not know about, to fill knowledge gaps."""
        chunks = await search_context_by_query(
            project_id,
            topic,
            top_k=5,
        )
        if not chunks:
            return f"No context found for '{topic}'."
        return (
            f"Project context for '{topic}':\n"
            + "\n---\n".join(chunks)
        )

    @tool
    async def find_code_reference(module_name: str) -> str:
        """Find relevant code files, modules, or services from the
        project context. Returns file paths, descriptions, and
        relationships when available in the indexed docs."""
        chunks = await search_context_by_query(
            project_id,
            f"file module service class {module_name} implementation",
            top_k=5,
        )
        keyword_chunks = await search_context_by_keyword(
            project_id,
            module_name,
            top_k=5,
        )
        all_chunks = list(dict.fromkeys(chunks + keyword_chunks))
        if not all_chunks:
            return f"No code references found for '{module_name}'."
        return (
            f"Code references for '{module_name}':\n"
            + "\n---\n".join(all_chunks[:7])
        )

    @tool
    async def suggest_pattern(requirement: str) -> str:
        """Search existing codebase documentation for implementation
        patterns that could be applied to the given requirement.
        Returns relevant code patterns and architectural approaches."""
        chunks = await search_context_by_query(
            project_id,
            f"pattern implementation approach design {requirement}",
            top_k=5,
        )
        if not chunks:
            return "No matching patterns found in project context."
        return (
            f"Implementation patterns for '{requirement}':\n"
            + "\n---\n".join(chunks)
        )

    @tool
    async def analyze_api_impact(change_description: str) -> str:
        """Evaluate the impact of a described change on the API
        surface. Searches for endpoints, contracts, and consumers
        that might be affected by the change."""
        chunks = await search_context_by_query(
            project_id,
            f"API endpoint route contract consumer {change_description}",
            top_k=5,
        )
        if not chunks:
            return "No API impact info found in project context."
        return (
            f"API impact context for '{change_description}':\n"
            + "\n---\n".join(chunks)
        )

    @tool
    async def check_test_coverage(module_name: str) -> str:
        """Search project context for test files, coverage info, and
        quality metrics related to the given module. Reports test
        status from indexed documentation."""
        chunks = await search_context_by_query(
            project_id,
            f"test coverage spec {module_name} pytest vitest",
            top_k=5,
        )
        keyword_hits = await search_context_by_keyword(
            project_id,
            f"test_{module_name}",
            top_k=3,
        )
        all_chunks = list(dict.fromkeys(chunks + keyword_hits))
        if not all_chunks:
            return f"No test coverage info found for '{module_name}'."
        return (
            f"Test context for '{module_name}':\n"
            + "\n---\n".join(all_chunks[:5])
        )

    return [
        search_project_context,
        find_code_reference,
        suggest_pattern,
        analyze_api_impact,
        check_test_coverage,
    ]
