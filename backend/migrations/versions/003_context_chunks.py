"""Add context_chunks table with vector column and HNSW index.

Revision ID: 003_context_chunks
Revises: 002_context_files
Create Date: 2026-03-27
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector
from sqlalchemy.dialects.postgresql import UUID

revision: str = "003_context_chunks"
down_revision: Union[str, None] = "002_context_files"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create context_chunks table with HNSW index."""
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.create_table(
        "context_chunks",
        sa.Column(
            "id",
            UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "context_file_id",
            UUID(as_uuid=True),
            sa.ForeignKey("context_files.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "project_id",
            UUID(as_uuid=True),
            sa.ForeignKey("projects.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("chunk_index", sa.Integer, nullable=False),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("embedding", Vector(1024), nullable=True),
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
    op.create_index("ix_context_chunks_project_id", "context_chunks", ["project_id"])
    op.create_index("ix_context_chunks_file_id", "context_chunks", ["context_file_id"])
    # HNSW index for cosine similarity search
    op.execute(
        "CREATE INDEX ix_context_chunks_embedding ON context_chunks "
        "USING hnsw (embedding vector_cosine_ops) WITH (m = 16, ef_construction = 64)"
    )


def downgrade() -> None:
    """Drop context_chunks table."""
    op.drop_index("ix_context_chunks_embedding")
    op.drop_index("ix_context_chunks_file_id")
    op.drop_index("ix_context_chunks_project_id")
    op.drop_table("context_chunks")
