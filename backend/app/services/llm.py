"""LLM service — OpenAI-compatible API client (Groq, OpenAI, local tower).

Provides both raw httpx client (legacy) and LangChain ChatOpenAI wrapper (agent pipeline).
"""

import json

import structlog
from httpx import AsyncClient
from langchain_openai import ChatOpenAI

from app.config import settings

logger = structlog.get_logger()


def get_chat_model(
    model: str | None = None,
    temperature: float = 0.3,
    max_tokens: int = 1024,
) -> ChatOpenAI:
    """Get a LangChain ChatOpenAI instance pointed at the configured LLM provider.

    Used by the agent pipeline for structured output and tool calling.
    """
    return ChatOpenAI(
        base_url=settings.llm_base_url,
        api_key=settings.llm_api_key,
        model=model or settings.llm_model,
        temperature=temperature,
        max_tokens=max_tokens,
    )

SYSTEM_PROMPT = """You are Cortex, a real-time AI copilot for software consultancy meetings.
Analyze transcription against project context. Be CONCISE.

Return JSON:
{
  "type": "alert" | "scope" | "suggestion",
  "summary": "Ultra-short preview (max 15 words)",
  "content": "Full explanation (2-3 sentences max)",
  "confidence": 0.0 to 1.0,
  "sources": ["relevant context snippet"]
}

Types:
- "alert": Technical conflict between what client says and project context.
  Example: "Cliente pide cambiar notificaciones pero NotificationDispatcher frozen hasta v3"
- "scope": Classify client request as scope actual or fuera de scope.
  Example summary: "✅ Scope actual — feature planificada Q2"
  Example summary: "⚠️ Fuera de scope — requiere nuevo presupuesto"
- "suggestion": Actionable info from context relevant to the conversation.
  Example: "En reunión anterior se acordó rate limiting a 100 req/s — no implementado aún"

If nothing noteworthy, return:
{"type": "none", "summary": "", "content": "", "confidence": 0, "sources": []}

Rules:
- NEVER repeat an insight already listed in "Previous Insights". Check before generating.
- ONLY generate if there's genuine value. Prefer "none" over low-quality output.
- Match the transcription language (usually Spanish).
- Keep confidence > 0.7 only when context strongly supports the insight.
- summary must be readable in a card title (max 15 words).
- content gives the full reasoning (max 3 sentences)."""


async def generate_insight(
    transcription: str,
    context_chunks: list[str],
    model: str | None = None,
    feedback_context: str = "",
    previous_insights: list[str] | None = None,
) -> dict | None:
    """Send transcription + context to LLM and parse insight JSON response."""
    if not settings.llm_api_key:
        logger.warning("llm_api_key_not_set", msg="Insight generation disabled")
        return None

    target_model = model or settings.llm_model
    context_text = (
        "\n---\n".join(context_chunks)
        if context_chunks
        else "No project context available."
    )
    previous_text = ""
    if previous_insights:
        previous_text = (
            "## Previous Insights (DO NOT repeat these)\n"
            + "\n".join(f"- {p}" for p in previous_insights[-5:])
            + "\n\n"
        )

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": (
                f"## Project Context\n{context_text}\n\n"
                f"{previous_text}"
                f"{'## User Feedback\n' + feedback_context + '\n\n' if feedback_context else ''}"
                f"## Meeting Transcription (last ~30 seconds)\n{transcription}\n\n"
                "Analyze and return a single JSON insight."
            ),
        },
    ]

    url = f"{settings.llm_base_url}/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {settings.llm_api_key}",
    }
    payload = {
        "model": target_model,
        "messages": messages,
        "temperature": 0.3,
        "max_tokens": 1024,
        "response_format": {"type": "json_object"},
    }

    try:
        async with AsyncClient(timeout=15.0) as client:
            response = await client.post(url, json=payload, headers=headers)

        if response.status_code == 429:
            logger.warning("llm_rate_limited", model=target_model)
            if target_model != settings.llm_fallback_model:
                return await generate_insight(
                    transcription,
                    context_chunks,
                    model=settings.llm_fallback_model,
                    previous_insights=previous_insights,
                )
            return None

        if response.status_code != 200:
            logger.error(
                "llm_api_error",
                status=response.status_code,
                body=response.text[:300],
            )
            return None

        data = response.json()
        raw_content = data["choices"][0]["message"]["content"]
        raw_insight = json.loads(raw_content)

        from app.schemas.insight import LLMInsightResponse

        validated = LLMInsightResponse.model_validate(raw_insight)

        if validated.type.value == "none":
            return None

        result = validated.model_dump()
        result["type"] = validated.type.value
        logger.info(
            "insight_generated",
            type=result["type"],
            summary=result.get("summary", "")[:50],
        )
        return result

    except json.JSONDecodeError:
        logger.warning("llm_invalid_json")
        return None
    except Exception:
        logger.exception("llm_request_failed")
        return None
