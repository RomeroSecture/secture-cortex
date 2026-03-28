"""User model."""

import enum
import uuid

from sqlalchemy import Enum, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class UserRole(str, enum.Enum):  # noqa: UP042 — StrEnum breaks SQLAlchemy enum serialization
    """Global user roles."""

    ADMIN = "admin"
    TECH_LEAD = "tech_lead"
    DEVELOPER = "developer"
    PM = "pm"
    COMMERCIAL = "commercial"


class User(Base, TimestampMixin):
    """User account."""

    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    email: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, name="user_role", values_callable=lambda x: [e.value for e in x]),
        default=UserRole.DEVELOPER,
        nullable=False,
    )

    project_memberships = relationship(
        "ProjectUser", back_populates="user", cascade="all, delete-orphan"
    )
