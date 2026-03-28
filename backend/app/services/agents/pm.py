"""PM specialist agent — scope, budget, roadmap, commitments, risk.

Uses create_react_agent with pgvector-backed tools for project-aware analysis.
"""

import json
import uuid

import structlog
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

from app.config import settings
from app.schemas.agent import AgentInsight, PipelineState
from app.services.agent_tools.pm_tools import create_pm_tools

logger = structlog.get_logger()

PM_PROMPT = (
    "You are the PM (Project Manager) agent in a real-time "
    "meeting copilot.\n"
    "You specialize in: scope classification, budget impact, "
    "roadmap conflicts, commitment tracking, and risk.\n"
    "\n"
    "You have tools to search the project's knowledge base. "
    "USE THEM to ground your insights in real project data.\n"
    "\n"
    "Your insight types:\n"
    '- "scope_classification": Classify request as '
    "{in-scope | planned | out-of-scope} x "
    "{low | medium | high effort}\n"
    '- "budget_impact": Accumulated effort estimate\n'
    '- "priority_conflict": Conflicts with roadmap items\n'
    '- "commitment_detected": Someone committed to a deadline\n'
    '- "commitment_collision": Incompatible commitments\n'
    '- "risk_escalation": Documented risk area detected\n'
    '- "scope_ceiling": Effort approaching threshold\n'
    "\n"
    "WORKFLOW:\n"
    "1. Read the transcription chunk\n"
    "2. If relevant, call tools to search for evidence\n"
    "3. Based on tool results, generate insights\n"
    "4. Return ONLY a JSON object with your insights\n"
    "\n"
    "Rules:\n"
    "- Be CONCISE: summary max 15 words, content max 3 sentences\n"
    '- Watch for commitment language ("lo tenemos para el viernes"'
    ', "me encargo de...")\n'
    "- Match transcription language (usually Spanish)\n"
    "- NEVER repeat insights from Previous Insights list\n"
    "\n"
    "Your FINAL response must be ONLY this JSON:\n"
    '{"insights": [{"type": "...", "subtype": "...", '
    '"summary": "...", "content": "...", '
    '"confidence": 0.8, "sources": ["..."]}]}\n'
    "Return empty array if nothing noteworthy: "
    '{"insights": []}'
)


def _get_specialist_model() -> ChatOpenAI:
    """Get the LLM configured for specialist agents."""
    return ChatOpenAI(
        base_url=settings.llm_base_url,
        api_key=settings.llm_api_key,
        model=settings.specialist_model,
        temperature=0.3,
        max_tokens=1024,
    )


def _parse_insights_from_response(content: str) -> list[dict]:
    """Extract insights JSON from agent's final response."""
    try:
        raw = json.loads(content)
        return raw.get("insights", [])
    except (json.JSONDecodeError, TypeError):
        start = content.find("{")
        end = content.rfind("}") + 1
        if start >= 0 and end > start:
            try:
                raw = json.loads(content[start:end])
                return raw.get("insights", [])
            except (json.JSONDecodeError, TypeError):
                pass
    return []


async def pm_node(state: PipelineState) -> dict:
    """Generate PM insights using ReAct agent with tools."""
    chunk = state["transcription_chunk"]
    project_id = uuid.UUID(state["project_id"])
    context_text = (
        "\n---\n".join(state["context_chunks"])
        if state["context_chunks"]
        else "Sin contexto disponible."
    )
    previous = state.get("previous_insights", [])
    previous_text = (
        "\n".join(f"- {p}" for p in previous[-5:])
        if previous
        else "Ninguno."
    )

    try:
        model = _get_specialist_model()
        tools = create_pm_tools(project_id)

        agent = create_react_agent(
            model=model,
            tools=tools,
            prompt=PM_PROMPT,
        )

        result = await agent.ainvoke({
            "messages": [{
                "role": "user",
                "content": (
                    f"## Project Context\n{context_text[:2000]}\n\n"
                    f"## Previous Insights (DO NOT repeat)\n"
                    f"{previous_text}\n\n"
                    f"## Transcription\n{chunk}\n\n"
                    "Analyze and respond with JSON insights."
                ),
            }],
        })

        final_msg = result["messages"][-1]
        content = (
            final_msg.content
            if hasattr(final_msg, "content")
            else str(final_msg)
        )
        insights_data = _parse_insights_from_response(content)

        insights = []
        for item in insights_data:
            insights.append(AgentInsight(
                agent_source="pm",
                type=item.get("type", "scope"),
                subtype=item.get("subtype", item.get("type", "")),
                summary=item.get("summary", ""),
                content=item.get("content", ""),
                confidence=item.get("confidence", 0.5),
                sources=item.get("sources", []),
                target_roles=["pm", "admin", "tech_lead"],
            ))

        logger.info("pm_generated", count=len(insights))
        return {"agent_insights": insights}

    except Exception:
        logger.exception("pm_agent_failed")
        return {"agent_insights": []}
