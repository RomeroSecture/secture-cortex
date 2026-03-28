"""Supervisor node — analyzes transcription chunk and routes to specialist agents."""

import json

import structlog
from langchain_openai import ChatOpenAI

from app.config import settings
from app.schemas.agent import PipelineState

logger = structlog.get_logger()

SUPERVISOR_SYSTEM_PROMPT = (
    "You are the Supervisor of a multi-agent copilot system for software "
    "consultancy meetings.\n"
    "Your job is to analyze each transcription chunk and decide which "
    "specialist agents should process it.\n"
    "\n"
    "Available agents:\n"
    "- **tech_lead**: Technical concerns — dependencies, architecture, "
    "effort estimation, tech debt, historical decisions\n"
    "- **pm**: Project management — scope classification, budget impact, "
    "roadmap conflicts, commitments, risk\n"
    "- **commercial**: Business opportunities — upsell signals, competitive "
    "mentions, client sentiment, service matching\n"
    "- **dev**: Implementation details — code references, patterns, API "
    "impact, test coverage, context gaps\n"
    "\n"
    "Rules:\n"
    "1. Activate ONLY agents relevant to the chunk content.\n"
    "2. You may activate 1 to 4 agents. Never zero.\n"
    '3. If casual/off-topic, activate only "dev".\n'
    "4. Classify the topic to help agents focus.\n"
    "\n"
    "Respond with ONLY this JSON:\n"
    '{"active_agents": ["tech_lead", "pm"], '
    '"topic_classification": "technical_scope", '
    '"reasoning": "Why these agents"}'
)

ALL_AGENTS = ["tech_lead", "pm", "commercial", "dev"]


def _get_supervisor_model() -> ChatOpenAI:
    """Get the LLM configured for the Supervisor node."""
    return ChatOpenAI(
        base_url=settings.llm_base_url,
        api_key=settings.llm_api_key,
        model=settings.supervisor_model,
        temperature=0.2,
        max_tokens=512,
        model_kwargs={"response_format": {"type": "json_object"}},
    )


async def supervisor_node(state: PipelineState) -> dict:
    """Analyze the transcription chunk and decide which agents to activate."""
    chunk = state["transcription_chunk"]
    context_preview = (
        "\n".join(state["context_chunks"][:2])
        if state["context_chunks"]
        else "Sin contexto."
    )

    try:
        model = _get_supervisor_model()
        response = await model.ainvoke([
            {"role": "system", "content": SUPERVISOR_SYSTEM_PROMPT},
            {
                "role": "user",
                "content": (
                    f"## Context Preview\n{context_preview[:500]}\n\n"
                    f"## Transcription Chunk\n{chunk}\n\n"
                    "Respond with JSON routing decision."
                ),
            },
        ])

        raw = json.loads(response.content)
        agents = raw.get("active_agents", ["dev"])
        topic = raw.get("topic_classification", "general")
        reasoning = raw.get("reasoning", "")

        valid_agents = [a for a in agents if a in ALL_AGENTS]
        if not valid_agents:
            valid_agents = ["dev"]

        logger.info(
            "supervisor_routed",
            agents=valid_agents,
            topic=topic,
            reasoning=reasoning[:100],
        )
        return {"active_agents": valid_agents}

    except Exception:
        logger.exception("supervisor_failed_fallback_to_dev")
        return {"active_agents": ["dev"]}
