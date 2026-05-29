"""Add street_address column to streets and buildings tables.

Revision ID: 0011
Revises: 0010
Create Date: 2026-03-23
"""
from alembic import op
import sqlalchemy as sa

revision = "0011"
down_revision = "0010"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "streets",
        sa.Column("street_address", sa.Text(), nullable=False, server_default=""),
    )
    op.add_column(
        "buildings",
        sa.Column("street_address", sa.Text(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("buildings", "street_address")
    op.drop_column("streets", "street_address")
