"""Add pilot_feedback table

Revision ID: 0003
Revises: 0002
Create Date: 2025-03-16 00:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0003"
down_revision: str | None = "0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "pilot_feedback",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("device_id", sa.Text(), nullable=False),
        sa.Column("submitted_by", sa.Text(), nullable=False),
        sa.Column("lga", sa.Text(), nullable=True),
        sa.Column("category", sa.Text(), nullable=True),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("metadata", postgresql.JSONB(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.PrimaryKeyConstraint("id", name="pilot_feedback_pkey"),
    )
    op.create_index("idx_pilot_feedback_lga", "pilot_feedback", ["lga"])
    op.create_index("idx_pilot_feedback_device", "pilot_feedback", ["device_id"])


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS idx_pilot_feedback_device")
    op.execute("DROP INDEX IF EXISTS idx_pilot_feedback_lga")
    op.drop_table("pilot_feedback")

