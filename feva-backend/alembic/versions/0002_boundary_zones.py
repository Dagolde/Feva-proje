"""Add boundary_zones table

Revision ID: 0002
Revises: 0001
Create Date: 2025-03-16 00:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0002"
down_revision: str | None = "0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # ── boundary_zones ────────────────────────────────────────────────────────
    op.create_table(
        "boundary_zones",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("zone_id", sa.Text(), nullable=False),
        sa.Column("zone_name", sa.Text(), nullable=False),
        sa.Column("zone_type", sa.Text(), nullable=False),
        sa.Column("lga_code", sa.Text(), nullable=True),
        sa.Column("ward_code", sa.Text(), nullable=True),
        sa.Column("postcode", sa.Text(), nullable=True),
        sa.Column(
            "geom",
            sa.Text(),  # placeholder; replaced below with PostGIS type
            nullable=False,
        ),
        sa.Column("shapefile_version", sa.Text(), nullable=False),
        sa.Column("shapefile_version_id", sa.Integer(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.ForeignKeyConstraint(
            ["shapefile_version_id"],
            ["shapefile_versions.id"],
            name="fk_boundary_zones_shapefile_version_id",
        ),
        sa.PrimaryKeyConstraint("id", name="boundary_zones_pkey"),
        sa.UniqueConstraint("zone_id", name="uq_boundary_zones_zone_id"),
    )
    # Replace placeholder with proper PostGIS MultiPolygon type.
    op.execute("ALTER TABLE boundary_zones DROP COLUMN geom")
    op.execute(
        "ALTER TABLE boundary_zones ADD COLUMN geom GEOMETRY(MultiPolygon, 4326) NOT NULL"
    )
    op.execute(
        "CREATE INDEX idx_boundary_zones_geom ON boundary_zones USING GIST(geom)"
    )
    op.create_index("idx_boundary_zones_layer", "boundary_zones", ["shapefile_version"])
    op.create_index("idx_boundary_zones_type", "boundary_zones", ["zone_type"])


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS idx_boundary_zones_type")
    op.execute("DROP INDEX IF EXISTS idx_boundary_zones_layer")
    op.execute("DROP INDEX IF EXISTS idx_boundary_zones_geom")
    op.drop_table("boundary_zones")

