"""Add meeting_outputs table for post-meeting intelligence.

Revision ID: 010_meeting_outputs
Revises: 009_conversation_intel
Create Date: 2026-03-28
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB, UUID

revision: str = "010_meeting_outputs"
down_revision: Union[str, None] = "009_conversation_intel"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create meeting_outputs table."""
    op.create_table(
        "meeting_outputs",
        sa.Column(
            "id", UUID(as_uuid=True), primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "meeting_id", UUID(as_uuid=True),
            sa.ForeignKey("meetings.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("type", sa.String(30), nullable=False),
        sa.Column("content", JSONB, nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True),
            server_default=sa.func.now(), nullable=False,
        ),
    )
    op.create_index(
        "ix_meeting_outputs_meeting_id",
        "meeting_outputs", ["meeting_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_meeting_outputs_meeting_id")
    op.drop_table("meeting_outputs")
