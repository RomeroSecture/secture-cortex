"""Conversation intelligence node — detects patterns beyond content.

Runs on EVERY transcription chunk in parallel with specialist agents.
Uses the fast model (Llama 3.1 8B) for low-latency pattern detection.
Single structured-output LLM call per chunk.
"""

import structlog
from langchain_openai import ChatOpenAI

from app.config import settings
from app.schemas.agent import AgentInsight, PipelineState
from app.schemas.conversation import ConversationIntelOutput

logger = structlog.get_logger()

CONVERSATION_INTEL_PROMPT = (
    "You are a conversation intelligence agent analyzing a live "
    "meeting transcription in real time.\n"
    "\n"
    "For EACH transcription chunk, detect:\n"
    "\n"
    "1. **Decision**: Language like 'decidimos que', 'quedamos en', "
    "'vamos a', 'entonces hacemos'. Extract what, who, context.\n"
    "\n"
    "2. **Action Item**: Commitments like 'yo me encargo de', "
    "'lo reviso para el viernes', 'te lo envío mañana'. "
    "Extract task, owner, deadline.\n"
    "\n"
    "3. **Question**: Unanswered questions. Extract question text "
    "and speaker.\n"
    "\n"
    "4. **Topic**: Classify the current conversation topic in "
    "1-3 words.\n"
    "\n"
    "5. **Sentiment**: Overall sentiment of this chunk "
    "(positive/neutral/negative, score -1 to 1).\n"
    "\n"
    "6. **Momentum keyword**: If a word/phrase is being repeated "
    "frequently (appears in context of previous chunks), note it.\n"
    "\n"
    "7. **Jargon**: Technical term that non-technical roles might "
    "not understand. Include a business-friendly translation.\n"
    "\n"
    "Rules:\n"
    "- Set fields to null if not detected in this chunk.\n"
    "- Be precise — only flag genuine detections.\n"
    "- Match the transcription language (usually Spanish).\n"
    "- Keep all text concise.\n"
    "\n"
    "Respond ONLY with this JSON structure:\n"
    "{\n"
    '  "decision": {"description": "...", "speaker": "...", '
    '"context": "..."} or null,\n'
    '  "action_item": {"task": "...", "owner": "...", '
    '"deadline": "..."} or null,\n'
    '  "question": {"question": "...", "speaker": "..."} or null,\n'
    '  "topic_label": "1-3 words",\n'
    '  "sentiment": {"topic": "...", "sentiment": '
    '"positive|neutral|negative", "score": -1.0 to 1.0} or null,\n'
    '  "momentum_keyword": "" or keyword,\n'
    '  "jargon_detected": "" or "term: explanation"\n'
    "}"
)


def _get_conversation_model() -> ChatOpenAI:
    """Get the fast LLM for conversation intelligence."""
    return ChatOpenAI(
        base_url=settings.llm_base_url,
        api_key=settings.llm_api_key,
        model=settings.conversation_model,
        temperature=0.1,
        max_tokens=512,
        model_kwargs={"response_format": {"type": "json_object"}},
    )


def _intel_to_insights(
    intel: ConversationIntelOutput,
) -> list[AgentInsight]:
    """Convert structured conversation intel to AgentInsight list."""
    insights: list[AgentInsight] = []

    if intel.decision:
        insights.append(AgentInsight(
            agent_source="conversation",
            type="alert",
            subtype="decision_detected",
            summary=intel.decision.description[:80],
            content=(
                f"Decisión: {intel.decision.description}. "
                f"Por: {intel.decision.speaker or 'no identificado'}."
            ),
            confidence=0.9,
            target_roles=[
                "admin", "tech_lead", "pm", "developer", "commercial",
            ],
            metadata=intel.decision.model_dump(),
        ))

    if intel.action_item:
        insights.append(AgentInsight(
            agent_source="conversation",
            type="alert",
            subtype="action_item",
            summary=(
                f"{intel.action_item.owner}: "
                f"{intel.action_item.task[:60]}"
            ),
            content=(
                f"Tarea: {intel.action_item.task}. "
                f"Responsable: {intel.action_item.owner}. "
                f"Fecha: {intel.action_item.deadline}."
            ),
            confidence=0.85,
            target_roles=[
                "admin", "tech_lead", "pm", "developer",
            ],
            metadata=intel.action_item.model_dump(),
        ))

    if intel.question:
        insights.append(AgentInsight(
            agent_source="conversation",
            type="suggestion",
            subtype="question_pending",
            summary=intel.question.question[:80],
            content=(
                f"Pregunta de {intel.question.speaker or 'alguien'}: "
                f"{intel.question.question}"
            ),
            confidence=0.7,
            target_roles=["admin", "tech_lead", "pm"],
            metadata=intel.question.model_dump(),
        ))

    if intel.jargon_detected:
        insights.append(AgentInsight(
            agent_source="conversation",
            type="suggestion",
            subtype="jargon_translation",
            summary=f"Término técnico: {intel.jargon_detected[:40]}",
            content=intel.jargon_detected,
            confidence=0.6,
            target_roles=["pm", "commercial"],
        ))

    if intel.momentum_keyword:
        insights.append(AgentInsight(
            agent_source="conversation",
            type="suggestion",
            subtype="momentum_alert",
            summary=(
                f"Tema recurrente: {intel.momentum_keyword}"
            ),
            content=(
                f"'{intel.momentum_keyword}' se repite. "
                "Posible preocupación no resuelta."
            ),
            confidence=0.65,
            target_roles=["admin", "tech_lead", "pm"],
        ))

    return insights


async def conversation_intel_node(
    state: PipelineState,
) -> dict:
    """Detect conversation patterns via single JSON call.

    Uses the fast model for low latency. Runs on every chunk.
    Manual JSON parse + Pydantic validation (Groq doesn't support json_schema).
    """
    chunk = state["transcription_chunk"]

    try:
        model = _get_conversation_model()
        response = await model.ainvoke([
            {"role": "system", "content": CONVERSATION_INTEL_PROMPT},
            {
                "role": "user",
                "content": (
                    f"## Transcription Chunk\n{chunk}\n\n"
                    "Analyze for conversation patterns. "
                    "Respond ONLY with JSON."
                ),
            },
        ])

        import json

        raw = json.loads(response.content)
        intel = ConversationIntelOutput.model_validate(raw)

        insights = _intel_to_insights(intel)
        logger.info(
            "conversation_intel_done",
            detections=len(insights),
            topic=intel.topic_label,
            sentiment=(
                intel.sentiment.sentiment
                if intel.sentiment
                else "none"
            ),
        )
        return {"agent_insights": insights}

    except Exception:
        logger.exception("conversation_intel_failed")
        return {"agent_insights": []}
