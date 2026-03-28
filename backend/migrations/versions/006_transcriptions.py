"""Add transcriptions table.

Revision ID: 006_transcriptions
Revises: 005_insights
Create Date: 2026-03-27
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision: str = "006_transcriptions"
down_revision: Union[str, None] = "005_insights"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create transcriptions table."""
    op.create_table(
        "transcriptions",
        sa.Column("id", UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("meeting_id", UUID(as_uuid=True),
                  sa.ForeignKey("meetings.id", ondelete="CASCADE"), nullable=False),
        sa.Column("speaker", sa.String(100), nullable=False),
        sa.Column("text", sa.Text, nullable=False),
        sa.Column("is_final", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("timestamp", sa.DateTime(timezone=True),
                  server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_transcriptions_meeting_id", "transcriptions", ["meeting_id"])


def downgrade() -> None:
    op.drop_index("ix_transcriptions_meeting_id")
    op.drop_table("transcriptions")
