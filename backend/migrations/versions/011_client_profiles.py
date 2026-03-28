"""Add client_profiles table for multi-meeting intelligence.

Revision ID: 011_client_profiles
Revises: 010_meeting_outputs
Create Date: 2026-03-28
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB, UUID

revision: str = "011_client_profiles"
down_revision: Union[str, None] = "010_meeting_outputs"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create client_profiles table."""
    op.create_table(
        "client_profiles",
        sa.Column(
            "id", UUID(as_uuid=True), primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "project_id", UUID(as_uuid=True),
            sa.ForeignKey("projects.id", ondelete="CASCADE"),
            nullable=False, unique=True,
        ),
        sa.Column(
            "behavior_data", JSONB, nullable=False,
            server_default="{}",
        ),
        sa.Column("health_score", sa.Float, nullable=True),
        sa.Column("health_trend", sa.String(10), nullable=True),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True),
            server_default=sa.func.now(), nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_table("client_profiles")
