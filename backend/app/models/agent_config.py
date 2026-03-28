"""Agent configuration model — per-project agent settings."""

import uuid

from sqlalchemy import Boolean, Float, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class AgentConfig(Base, TimestampMixin):
    """Per-project configuration for a specialist agent."""

    __tablename__ = "agent_configs"
    __table_args__ = (
        UniqueConstraint("project_id", "agent_type", name="uq_agent_config_project_type"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
    )
    agent_type: Mapped[str] = mapped_column(
        String(20), nullable=False,
    )
    system_prompt_override: Mapped[str | None] = mapped_column(
        Text, nullable=True,
    )
    confidence_threshold: Mapped[float] = mapped_column(
        Float, nullable=False, default=0.7,
    )
    enabled: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True,
    )
    tools_config: Mapped[dict | None] = mapped_column(
        JSONB, nullable=True,
    )
