"""Add boundary_discrepancies table

Revision ID: 0009
Revises: 0008
Create Date: 2026-03-24

Requirements: 21.1, 21.2, 21.7
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0009"
down_revision: str | None = "0008"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "boundary_discrepancies",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("postcode_polygon_id", sa.Text(), nullable=False),
        sa.Column("admin_polygon_id", sa.Text(), nullable=False),
        sa.Column("admin_type", sa.Text(), nullable=False),
        sa.Column("overlap_area_m2", sa.Numeric(18, 4), nullable=False),
        sa.Column("shapefile_version_id", sa.Integer(), nullable=True),
        sa.Column(
            "detected_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.CheckConstraint(
            "admin_type IN ('lga','ward')",
            name="ck_boundary_discrepancies_admin_type",
        ),
        sa.ForeignKeyConstraint(
            ["shapefile_version_id"],
            ["shapefile_versions.id"],
            name="fk_boundary_discrepancies_shapefile_version_id",
        ),
        sa.PrimaryKeyConstraint("id", name="boundary_discrepancies_pkey"),
    )
    op.create_index(
        "idx_boundary_discrepancies_postcode",
        "boundary_discrepancies",
        ["postcode_polygon_id"],
    )
    op.create_index(
        "idx_boundary_discrepancies_admin",
        "boundary_discrepancies",
        ["admin_polygon_id", "admin_type"],
    )
    op.create_index(
        "idx_boundary_discrepancies_detected",
        "boundary_discrepancies",
        ["detected_at"],
    )


def downgrade() -> None:
    op.drop_index("idx_boundary_discrepancies_detected", table_name="boundary_discrepancies")
    op.drop_index("idx_boundary_discrepancies_admin", table_name="boundary_discrepancies")
    op.drop_index("idx_boundary_discrepancies_postcode", table_name="boundary_discrepancies")
    op.drop_table("boundary_discrepancies")
