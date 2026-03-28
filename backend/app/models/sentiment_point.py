"""SentimentPoint model — per-topic sentiment tracking."""

import uuid

from sqlalchemy import DateTime, Float, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class SentimentPoint(Base):
    """A sentiment data point from a meeting conversation."""

    __tablename__ = "sentiment_points"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    meeting_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("meetings.id", ondelete="CASCADE"),
        nullable=False,
    )
    topic: Mapped[str | None] = mapped_column(
        String(200), nullable=True,
    )
    sentiment: Mapped[str] = mapped_column(
        String(10), nullable=False,
    )
    score: Mapped[float] = mapped_column(
        Float, nullable=False,
    )
    timestamp = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
