"""Project and project membership models."""

import enum
import uuid

from sqlalchemy import Enum, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class ProjectRole(str, enum.Enum):  # noqa: UP042 — StrEnum breaks SQLAlchemy enum serialization
    """Roles within a project."""

    ADMIN = "admin"
    TECH_LEAD = "tech_lead"
    DEVELOPER = "developer"
    PM = "pm"
    COMMERCIAL = "commercial"


class Project(Base, TimestampMixin):
    """Client project."""

    __tablename__ = "projects"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    members = relationship(
        "ProjectUser", back_populates="project", cascade="all, delete-orphan"
    )


class ProjectUser(Base, TimestampMixin):
    """Association: user membership in a project with a role."""

    __tablename__ = "project_users"
    __table_args__ = (
        UniqueConstraint("project_id", "user_id", name="uq_project_user"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    role_in_project: Mapped[ProjectRole] = mapped_column(
        Enum(ProjectRole, name="project_role", values_callable=lambda x: [e.value for e in x]),
        nullable=False,
    )

    project = relationship("Project", back_populates="members")
    user = relationship("User", back_populates="project_memberships")
