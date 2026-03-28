"""ClientProfile model — per-project behavioral profiling across meetings."""

import uuid

from sqlalchemy import DateTime, Float, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class ClientProfile(Base):
    """Accumulated client behavior profile for a project."""

    __tablename__ = "client_profiles"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    behavior_data: Mapped[dict] = mapped_column(
        JSONB, nullable=False, default=dict,
    )
    health_score: Mapped[float | None] = mapped_column(
        Float, nullable=True,
    )
    health_trend: Mapped[str | None] = mapped_column(
        String(10), nullable=True,
    )
    updated_at = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
