"""Insight and InsightFeedback models — AI-generated meeting insights."""

import enum
import uuid

from sqlalchemy import Enum, Float, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class InsightType(str, enum.Enum):  # noqa: UP042
    """Types of AI-generated insights."""

    ALERT = "alert"
    SCOPE = "scope"
    SUGGESTION = "suggestion"


class FeedbackRating(str, enum.Enum):  # noqa: UP042
    """User feedback rating on an insight."""

    USEFUL = "useful"
    NOT_USEFUL = "not_useful"
    DISMISSED = "dismissed"


class Insight(Base, TimestampMixin):
    """An AI-generated insight from a meeting."""

    __tablename__ = "insights"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    meeting_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("meetings.id", ondelete="CASCADE"),
        nullable=False,
    )
    type: Mapped[InsightType] = mapped_column(
        Enum(InsightType, name="insight_type", values_callable=lambda x: [e.value for e in x]),
        nullable=False,
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    sources: Mapped[list[str]] = mapped_column(ARRAY(Text), nullable=False, default=list)

    # Epic 7: Multi-agent pipeline metadata
    agent_source: Mapped[str | None] = mapped_column(
        String(20), nullable=True,
    )
    target_roles: Mapped[list[str] | None] = mapped_column(
        ARRAY(Text), nullable=True,
    )
    insight_subtype: Mapped[str | None] = mapped_column(
        String(50), nullable=True,
    )


class InsightFeedback(Base, TimestampMixin):
    """User feedback on an insight."""

    __tablename__ = "insight_feedback"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    insight_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("insights.id", ondelete="CASCADE"),
        nullable=False,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    rating: Mapped[FeedbackRating] = mapped_column(
        Enum(
            FeedbackRating,
            name="feedback_rating",
            values_callable=lambda x: [e.value for e in x],
        ),
        nullable=False,
    )
