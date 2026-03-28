"""Supervisor node — analyzes transcription chunk and routes to specialist agents."""

import structlog
from langchain_openai import ChatOpenAI

from app.config import settings
from app.schemas.agent import PipelineState, SupervisorDecision

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
    "1. Activate ONLY agents whose specialization is relevant to the chunk content.\n"
    "2. You may activate 1 to 4 agents. Never activate zero — "
    "at minimum activate the most relevant one.\n"
    "3. If the chunk is purely casual/off-topic, activate only \"dev\" "
    "as a fallback for context awareness.\n"
    "4. Classify the topic to help agents focus.\n"
    "5. Respond in the language of the transcription (usually Spanish).\n"
    "\n"
    "Analyze the transcription and respond with your routing decision."
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
    )


async def supervisor_node(state: PipelineState) -> dict:
    """Analyze the transcription chunk and decide which agents to activate.

    Returns a state update with active_agents set.
    """
    chunk = state["transcription_chunk"]
    context_preview = (
        "\n".join(state["context_chunks"][:2])
        if state["context_chunks"]
        else "Sin contexto."
    )

    try:
        model = _get_supervisor_model().with_structured_output(SupervisorDecision)
        decision: SupervisorDecision = await model.ainvoke([
            {"role": "system", "content": SUPERVISOR_SYSTEM_PROMPT},
            {
                "role": "user",
                "content": (
                    f"## Context Preview\n{context_preview[:500]}\n\n"
                    f"## Transcription Chunk\n{chunk}\n\n"
                    "Decide which agents to activate."
                ),
            },
        ])

        # Validate agent names — only allow known agents
        valid_agents = [a for a in decision.active_agents if a in ALL_AGENTS]
        if not valid_agents:
            valid_agents = ["dev"]

        logger.info(
            "supervisor_routed",
            agents=valid_agents,
            topic=decision.topic_classification,
            reasoning=decision.reasoning[:100],
        )
        return {"active_agents": valid_agents}

    except Exception:
        logger.exception("supervisor_failed_fallback_to_dev")
        return {"active_agents": ["dev"]}
