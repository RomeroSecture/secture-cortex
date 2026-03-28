"""Meeting model — live meeting sessions linked to projects."""

import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class MeetingStatus(str, enum.Enum):  # noqa: UP042
    """Meeting lifecycle status."""

    RECORDING = "recording"
    ENDED = "ended"


class Meeting(Base, TimestampMixin):
    """A meeting session linked to a project."""

    __tablename__ = "meetings"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    status: Mapped[MeetingStatus] = mapped_column(
        Enum(
            MeetingStatus,
            name="meeting_status",
            values_callable=lambda x: [e.value for e in x],
        ),
        default=MeetingStatus.RECORDING,
        nullable=False,
    )
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    ended_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    project = relationship("Project")
