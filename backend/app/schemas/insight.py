"""Pydantic v2 schemas for insight validation and API responses."""

import uuid
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class InsightTypeEnum(str, Enum):  # noqa: UP042 — StrEnum breaks SQLAlchemy
    """Insight types returned by the LLM."""

    ALERT = "alert"
    SCOPE = "scope"
    SUGGESTION = "suggestion"
    NONE = "none"


class LLMInsightResponse(BaseModel):
    """Schema to validate the raw JSON response from the LLM."""

    summary: str = ""

    type: InsightTypeEnum
    content: str = ""
    confidence: float = Field(ge=0.0, le=1.0, default=0.0)
    sources: list[str] = Field(default_factory=list)


class InsightResponse(BaseModel):
    """API response schema for an insight."""

    id: uuid.UUID
    meeting_id: uuid.UUID
    type: str
    content: str
    confidence: float
    sources: list[str]
    agent_source: str | None = None
    target_roles: list[str] | None = None
    insight_subtype: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class InsightListResponse(BaseModel):
    """Response wrapper for insight list."""

    data: list[InsightResponse]


class FeedbackCreate(BaseModel):
    """Request schema for submitting feedback on an insight."""

    rating: str = Field(pattern=r"^(useful|not_useful|dismissed)$")


class FeedbackResponse(BaseModel):
    """Response data for feedback submission."""

    insight_id: uuid.UUID
    rating: str


class FeedbackDetailResponse(BaseModel):
    """Wrapped response for feedback submission."""

    data: FeedbackResponse
