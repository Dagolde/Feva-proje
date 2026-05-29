"""Add spatial indexes on buildings and streets geometry columns

Revision ID: 0010
Revises: 0009
Create Date: 2025-03-23

Adds GIST spatial indexes so ST_DWithin duplicate detection and
map-based queries don't do full table scans.

Requirements: 11.2, 11.3
"""
from alembic import op

revision = '0010'
down_revision = '0009'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Spatial index on buildings geometry (speeds up ST_DWithin duplicate check)
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_buildings_geom ON buildings USING GIST (geom)"
    )
    # Spatial index on streets geometry
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_streets_geom ON streets USING GIST (geom)"
    )
    # Index on buildings.building_id for idempotency lookup
    op.create_index(
        'idx_buildings_building_id',
        'buildings',
        ['building_id'],
    )
    # Index on streets.street_id for idempotency lookup
    op.create_index(
        'idx_streets_street_id',
        'streets',
        ['street_id'],
    )
    # Index on buildings.device_local_id for photo linking
    op.create_index(
        'idx_buildings_device_local_id',
        'buildings',
        ['device_local_id'],
    )
    # Index on streets.device_local_id for photo linking
    op.create_index(
        'idx_streets_device_local_id',
        'streets',
        ['device_local_id'],
    )


def downgrade() -> None:
    op.drop_index('idx_streets_device_local_id', table_name='streets')
    op.drop_index('idx_buildings_device_local_id', table_name='buildings')
    op.drop_index('idx_streets_street_id', table_name='streets')
    op.drop_index('idx_buildings_building_id', table_name='buildings')
    op.execute("DROP INDEX IF EXISTS idx_streets_geom")
    op.execute("DROP INDEX IF EXISTS idx_buildings_geom")
