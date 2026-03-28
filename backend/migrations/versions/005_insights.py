"""Add insights and insight_feedback tables.

Revision ID: 005_insights
Revises: 004_meetings
Create Date: 2026-03-27
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ARRAY, UUID

revision: str = "005_insights"
down_revision: Union[str, None] = "004_meetings"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create insights and insight_feedback tables."""
    op.create_table(
        "insights",
        sa.Column("id", UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("meeting_id", UUID(as_uuid=True),
                  sa.ForeignKey("meetings.id", ondelete="CASCADE"), nullable=False),
        sa.Column("type", sa.Enum("alert", "scope", "suggestion",
                  name="insight_type"), nullable=False),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("confidence", sa.Float, nullable=False),
        sa.Column("sources", ARRAY(sa.Text), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True),
                  server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True),
                  server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_insights_meeting_id", "insights", ["meeting_id"])

    op.create_table(
        "insight_feedback",
        sa.Column("id", UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("insight_id", UUID(as_uuid=True),
                  sa.ForeignKey("insights.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", UUID(as_uuid=True),
                  sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("rating", sa.Enum("useful", "not_useful", "dismissed",
                  name="feedback_rating"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True),
                  server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True),
                  server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_insight_feedback_insight_id", "insight_feedback", ["insight_id"])


def downgrade() -> None:
    op.drop_index("ix_insight_feedback_insight_id")
    op.drop_table("insight_feedback")
    op.drop_index("ix_insights_meeting_id")
    op.drop_table("insights")
    op.execute("DROP TYPE IF EXISTS feedback_rating")
    op.execute("DROP TYPE IF EXISTS insight_type")
