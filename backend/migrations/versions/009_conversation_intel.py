"""Add conversation_events and sentiment_points tables.

Revision ID: 009_conversation_intel
Revises: 008_agent_pipeline
Create Date: 2026-03-28
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB, UUID

revision: str = "009_conversation_intel"
down_revision: Union[str, None] = "008_agent_pipeline"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create conversation_events and sentiment_points tables."""
    op.create_table(
        "conversation_events",
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
            "detected_at", sa.DateTime(timezone=True),
            server_default=sa.func.now(), nullable=False,
        ),
        sa.Column(
            "resolved", sa.Boolean, nullable=False,
            server_default="false",
        ),
    )
    op.create_index(
        "ix_conversation_events_meeting_id",
        "conversation_events", ["meeting_id"],
    )

    op.create_table(
        "sentiment_points",
        sa.Column(
            "id", UUID(as_uuid=True), primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "meeting_id", UUID(as_uuid=True),
            sa.ForeignKey("meetings.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("topic", sa.String(200), nullable=True),
        sa.Column("sentiment", sa.String(10), nullable=False),
        sa.Column("score", sa.Float, nullable=False),
        sa.Column(
            "timestamp", sa.DateTime(timezone=True),
            server_default=sa.func.now(), nullable=False,
        ),
    )
    op.create_index(
        "ix_sentiment_points_meeting_id",
        "sentiment_points", ["meeting_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_sentiment_points_meeting_id")
    op.drop_table("sentiment_points")
    op.drop_index("ix_conversation_events_meeting_id")
    op.drop_table("conversation_events")
