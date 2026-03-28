"""Add context_files table.

Revision ID: 002_context_files
Revises: 001_initial
Create Date: 2026-03-27
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision: str = "002_context_files"
down_revision: Union[str, None] = "001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create context_files table."""
    op.create_table(
        "context_files",
        sa.Column(
            "id",
            UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "project_id",
            UUID(as_uuid=True),
            sa.ForeignKey("projects.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("filename", sa.String(500), nullable=False),
        sa.Column("file_size", sa.BigInteger, nullable=False),
        sa.Column("content_type", sa.String(100), nullable=False),
        sa.Column("raw_content", sa.Text, nullable=False, server_default=""),
        sa.Column(
            "status",
            sa.Enum("pending", "indexing", "indexed", "error", name="file_status"),
            nullable=False,
            server_default="pending",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index("ix_context_files_project_id", "context_files", ["project_id"])


def downgrade() -> None:
    """Drop context_files table."""
    op.drop_index("ix_context_files_project_id")
    op.drop_table("context_files")
    op.execute("DROP TYPE IF EXISTS file_status")
