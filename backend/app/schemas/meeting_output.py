"""Pydantic v2 schemas for post-meeting intelligence outputs."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

# ─── Structured output schemas (LLM responses) ────────────────


class MinutesOutput(BaseModel):
    """Structured meeting minutes generated post-meeting."""

    attendees: list[str] = Field(default_factory=list)
    topics_covered: list[str] = Field(default_factory=list)
    decisions: list[dict] = Field(default_factory=list)
    action_items: list[dict] = Field(default_factory=list)
    client_requests: list[dict] = Field(default_factory=list)
    risks_detected: list[str] = Field(default_factory=list)
    unanswered_questions: list[str] = Field(default_factory=list)
    next_steps: list[str] = Field(default_factory=list)
    summary: str = ""


class HandoffOutput(BaseModel):
    """Handoff package for the next meeting."""

    topic_status: list[dict] = Field(default_factory=list)
    pending_commitments: list[dict] = Field(default_factory=list)
    open_questions: list[str] = Field(default_factory=list)
    context_for_next: str = ""


class SprintImpactOutput(BaseModel):
    """Sprint impact assessment from meeting requests."""

    total_requests: int = 0
    estimated_days: float = 0.0
    displaced_stories: list[str] = Field(default_factory=list)
    recommendation: str = ""


class EmailDraftOutput(BaseModel):
    """Client follow-up email draft."""

    subject: str = ""
    greeting: str = ""
    body: str = ""
    commitments: list[str] = Field(default_factory=list)
    next_steps: list[str] = Field(default_factory=list)
    closing: str = ""


class BriefingOutput(BaseModel):
    """Internal team briefing for absent members."""

    summary: str = ""
    changes_for_team: list[str] = Field(default_factory=list)
    relevant_action_items: list[dict] = Field(default_factory=list)
    key_decisions: list[str] = Field(default_factory=list)


class RetrospectiveOutput(BaseModel):
    """Meeting retrospective analytics."""

    duration_minutes: int = 0
    scope_ratio: str = ""
    insights_generated: int = 0
    action_items_count: int = 0
    sentiment_summary: str = ""
    comparison_note: str = ""


# ─── API response schemas ─────────────────────────────────────


class MeetingOutputResponse(BaseModel):
    """API response for a single meeting output."""

    id: uuid.UUID
    meeting_id: uuid.UUID
    type: str
    content: dict
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MeetingOutputListResponse(BaseModel):
    """API response wrapping a list of meeting outputs."""

    data: list[MeetingOutputResponse]
