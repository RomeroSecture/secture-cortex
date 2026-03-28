"""Make context_chunks.context_file_id nullable for meeting transcription chunks.

Revision ID: 007_nullable_chunk_file_id
Revises: 006_transcriptions
Create Date: 2026-03-27
"""
from typing import Sequence, Union

from alembic import op

revision: str = "007_nullable_chunk_file_id"
down_revision: Union[str, None] = "006_transcriptions"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column("context_chunks", "context_file_id", nullable=True)


def downgrade() -> None:
    op.alter_column("context_chunks", "context_file_id", nullable=False)
