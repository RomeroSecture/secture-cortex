"""Post-meeting intelligence — generates outputs when a meeting ends.

Produces 6 structured outputs via LLM calls:
minutes, handoff, sprint_impact, email_draft, briefing, retrospective.
Runs sequentially (not real-time, no latency pressure).
"""

import uuid

import structlog
from langchain_openai import ChatOpenAI
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.insight import Insight
from app.models.meeting_output import MeetingOutput
from app.models.transcription import Transcription
from app.schemas.meeting_output import (
    BriefingOutput,
    EmailDraftOutput,
    HandoffOutput,
    MinutesOutput,
    RetrospectiveOutput,
    SprintImpactOutput,
)

logger = structlog.get_logger()

# Output definitions: type → (Pydantic schema, model name, system prompt)
OUTPUT_CONFIGS: list[tuple[str, type, str, str]] = [
    (
        "minutes",
        MinutesOutput,
        settings.llm_model,
        (
            "Generate structured meeting minutes in Spanish. "
            "Include: attendees (speakers detected), topics covered, "
            "decisions (with owner), action items (owner + deadline), "
            "client requests (classified by scope), risks detected, "
            "unanswered questions, and next steps. Be comprehensive."
        ),
    ),
    (
        "handoff",
        HandoffOutput,
        settings.llm_model,
        (
            "Generate a handoff package for the next meeting in Spanish. "
            "Include: status of each topic discussed, pending commitments, "
            "open questions, and context needed for the next session."
        ),
    ),
    (
        "sprint_impact",
        SprintImpactOutput,
        settings.llm_fallback_model,
        (
            "Analyze the meeting for sprint impact in Spanish. "
            "Count new requests, estimate total effort in dev-days, "
            "list stories that would be displaced, and recommend "
            "whether reprioritization is needed."
        ),
    ),
    (
        "email_draft",
        EmailDraftOutput,
        settings.llm_model,
        (
            "Draft a professional follow-up email to the client in "
            "Spanish. Include: meeting summary, team commitments with "
            "dates, requests requiring additional proposals, and "
            "next steps. Tone: professional but warm."
        ),
    ),
    (
        "briefing",
        BriefingOutput,
        settings.llm_fallback_model,
        (
            "Generate an internal team briefing in Spanish for members "
            "who were NOT in the meeting. Include: what was discussed "
            "(summary), what changes for their work, action items that "
            "affect them, and key decisions they need to know."
        ),
    ),
    (
        "retrospective",
        RetrospectiveOutput,
        settings.llm_fallback_model,
        (
            "Generate meeting retrospective analytics in Spanish. "
            "Include: duration, scope ratio (in-scope vs out-of-scope), "
            "insights generated count, action items count, sentiment "
            "summary, and comparison notes if context available."
        ),
    ),
]


def _get_model(model_name: str) -> ChatOpenAI:
    """Get an LLM instance for post-meeting generation."""
    return ChatOpenAI(
        base_url=settings.llm_base_url,
        api_key=settings.llm_api_key,
        model=model_name,
        temperature=0.3,
        max_tokens=4096,
        model_kwargs={"response_format": {"type": "json_object"}},
    )


async def _get_meeting_context(
    db: AsyncSession,
    meeting_id: uuid.UUID,
) -> str:
    """Gather full transcription + insights as context for generation."""
    # Transcription
    result = await db.execute(
        select(Transcription)
        .where(Transcription.meeting_id == meeting_id)
        .order_by(Transcription.timestamp)
    )
    segments = result.scalars().all()
    transcription = "\n".join(
        f"[{s.speaker}]: {s.text}" for s in segments
    )

    # Insights
    result = await db.execute(
        select(Insight)
        .where(Insight.meeting_id == meeting_id)
        .order_by(Insight.created_at)
    )
    insights = result.scalars().all()
    insights_text = "\n".join(
        f"- [{i.type.value}] {i.content}" for i in insights
    )

    return (
        f"## Full Transcription\n{transcription or 'Sin transcripción.'}"
        f"\n\n## Insights Generated\n{insights_text or 'Ninguno.'}"
    )


async def generate_post_meeting_outputs(
    db: AsyncSession,
    meeting_id: uuid.UUID,
) -> list[MeetingOutput]:
    """Generate all post-meeting outputs and persist them.

    Runs sequentially (not real-time). Each output is a single
    structured LLM call stored in the meeting_outputs table.
    """
    context = await _get_meeting_context(db, meeting_id)
    if not context.strip():
        logger.warning(
            "post_meeting_no_context",
            meeting_id=str(meeting_id),
        )
        return []

    outputs: list[MeetingOutput] = []

    for output_type, schema_cls, model_name, system_prompt in OUTPUT_CONFIGS:
        try:
            model = _get_model(model_name)
            response = await model.ainvoke([
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": (
                        f"{context}\n\n"
                        "Respond ONLY with JSON."
                    ),
                },
            ])

            import json as _json

            raw = _json.loads(response.content)
            result = schema_cls.model_validate(raw)

            output = MeetingOutput(
                meeting_id=meeting_id,
                type=output_type,
                content=result.model_dump(),
            )
            db.add(output)
            outputs.append(output)

            logger.info(
                "post_meeting_output_generated",
                meeting_id=str(meeting_id),
                type=output_type,
            )

        except Exception:
            logger.exception(
                "post_meeting_output_failed",
                meeting_id=str(meeting_id),
                type=output_type,
            )

    if outputs:
        await db.commit()
        logger.info(
            "post_meeting_complete",
            meeting_id=str(meeting_id),
            outputs=len(outputs),
        )

    return outputs
