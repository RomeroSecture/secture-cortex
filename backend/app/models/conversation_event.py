"""ConversationEvent model — detected conversation patterns."""

import uuid

from sqlalchemy import Boolean, DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class ConversationEvent(Base):
    """A conversation intelligence detection from a meeting."""

    __tablename__ = "conversation_events"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    meeting_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("meetings.id", ondelete="CASCADE"),
        nullable=False,
    )
    type: Mapped[str] = mapped_column(
        String(30), nullable=False,
    )
    content: Mapped[dict] = mapped_column(
        JSONB, nullable=False,
    )
    detected_at = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    resolved: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False,
    )
