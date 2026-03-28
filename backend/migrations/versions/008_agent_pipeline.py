"""Add agent_configs table and agent pipeline columns to insights.

Revision ID: 008_agent_pipeline
Revises: 007_nullable_chunk_file_id
Create Date: 2026-03-28
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID

revision: str = "008_agent_pipeline"
down_revision: Union[str, None] = "007_nullable_chunk_file_id"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create agent_configs table and add columns to insights."""
    # agent_configs table
    op.create_table(
        "agent_configs",
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
        sa.Column("agent_type", sa.String(20), nullable=False),
        sa.Column("system_prompt_override", sa.Text, nullable=True),
        sa.Column("confidence_threshold", sa.Float, nullable=False, server_default="0.7"),
        sa.Column("enabled", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("tools_config", JSONB, nullable=True),
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
        sa.UniqueConstraint("project_id", "agent_type", name="uq_agent_config_project_type"),
    )
    op.create_index("ix_agent_configs_project_id", "agent_configs", ["project_id"])

    # Add agent pipeline columns to insights table
    op.add_column("insights", sa.Column("agent_source", sa.String(20), nullable=True))
    op.add_column("insights", sa.Column("target_roles", ARRAY(sa.Text), nullable=True))
    op.add_column("insights", sa.Column("insight_subtype", sa.String(50), nullable=True))


def downgrade() -> None:
    op.drop_column("insights", "insight_subtype")
    op.drop_column("insights", "target_roles")
    op.drop_column("insights", "agent_source")
    op.drop_index("ix_agent_configs_project_id")
    op.drop_table("agent_configs")
