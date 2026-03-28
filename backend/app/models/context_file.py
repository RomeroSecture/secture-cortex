"""ContextFile model — uploaded project knowledge base documents."""

import enum
import uuid

from sqlalchemy import BigInteger, Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class FileStatus(str, enum.Enum):  # noqa: UP042 — StrEnum breaks SQLAlchemy enum serialization
    """Processing status of a context file."""

    PENDING = "pending"
    INDEXING = "indexing"
    INDEXED = "indexed"
    ERROR = "error"


class ContextFile(Base, TimestampMixin):
    """A file uploaded as project context for the RAG pipeline."""

    __tablename__ = "context_files"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
    )
    filename: Mapped[str] = mapped_column(String(500), nullable=False)
    file_size: Mapped[int] = mapped_column(BigInteger, nullable=False)
    content_type: Mapped[str] = mapped_column(String(100), nullable=False)
    raw_content: Mapped[str] = mapped_column(Text, nullable=False, default="")
    status: Mapped[FileStatus] = mapped_column(
        Enum(FileStatus, name="file_status", values_callable=lambda x: [e.value for e in x]),
        default=FileStatus.PENDING,
        nullable=False,
    )

    project = relationship("Project")
