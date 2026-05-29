"""Initial schema

Revision ID: 0001
Revises:
Create Date: 2024-01-01 00:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # ── Extensions ────────────────────────────────────────────────────────────
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis")
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")

    # ── roles ─────────────────────────────────────────────────────────────────
    op.create_table(
        "roles",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint("id", name="roles_pkey"),
        sa.UniqueConstraint("name", name="uq_roles_name"),
    )

    # ── users ─────────────────────────────────────────────────────────────────
    op.create_table(
        "users",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("username", sa.Text(), nullable=False),
        sa.Column("email", sa.Text(), nullable=False),
        sa.Column("password_hash", sa.Text(), nullable=False),
        sa.Column("role_id", sa.Integer(), nullable=False),
        sa.Column("lga_assignment", postgresql.ARRAY(sa.Text()), nullable=True),
        sa.Column("totp_secret", sa.Text(), nullable=True),
        sa.Column("totp_enabled", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("failed_attempts", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("locked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.ForeignKeyConstraint(["role_id"], ["roles.id"], name="fk_users_role_id"),
        sa.PrimaryKeyConstraint("id", name="users_pkey"),
        sa.UniqueConstraint("username", name="uq_users_username"),
        sa.UniqueConstraint("email", name="uq_users_email"),
    )
    op.create_index("idx_users_role", "users", ["role_id"])

    # ── dropdown_config ───────────────────────────────────────────────────────
    op.create_table(
        "dropdown_config",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("category", sa.Text(), nullable=False),
        sa.Column("value", sa.Text(), nullable=False),
        sa.Column("label", sa.Text(), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.ForeignKeyConstraint(
            ["created_by"], ["users.id"], name="fk_dropdown_config_created_by"
        ),
        sa.PrimaryKeyConstraint("id", name="dropdown_config_pkey"),
        sa.UniqueConstraint(
            "category", "value", name="uq_dropdown_config_category_value"
        ),
    )

    # ── shapefile_versions ────────────────────────────────────────────────────
    op.create_table(
        "shapefile_versions",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("layer_name", sa.Text(), nullable=False),
        sa.Column("version_tag", sa.Text(), nullable=False),
        sa.Column("checksum_sha256", sa.Text(), nullable=False),
        sa.Column("uploaded_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column(
            "uploaded_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.ForeignKeyConstraint(
            ["uploaded_by"], ["users.id"], name="fk_shapefile_versions_uploaded_by"
        ),
        sa.PrimaryKeyConstraint("id", name="shapefile_versions_pkey"),
    )

    # ── streets ───────────────────────────────────────────────────────────────
    op.create_table(
        "streets",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("street_id", sa.Text(), nullable=False),
        sa.Column("street_name", sa.Text(), nullable=False),
        sa.Column("street_type", sa.Text(), nullable=False),
        sa.Column("surface_type", sa.Text(), nullable=False),
        sa.Column("street_condition", sa.Text(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column(
            "geom",
            sa.Text(),  # placeholder; actual type set via raw SQL below
            nullable=False,
        ),
        sa.Column("zone", sa.Text(), nullable=True),
        sa.Column("lga", sa.Text(), nullable=False),
        sa.Column("ward", sa.Text(), nullable=True),
        sa.Column("enumerator_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("enumeration_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "verification_status",
            sa.Text(),
            nullable=False,
            server_default="pending",
        ),
        sa.Column("reviewed_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("rejection_reason", sa.Text(), nullable=True),
        sa.Column("boundary_flag", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column(
            "gps_accuracy_flag", sa.Boolean(), nullable=False, server_default="false"
        ),
        sa.Column("qa_flags", postgresql.JSONB(), nullable=True),
        sa.Column("device_local_id", sa.Integer(), nullable=True),
        sa.Column("device_id", sa.Text(), nullable=True),
        sa.Column(
            "synced_at",
            sa.DateTime(timezone=True),
            nullable=True,
            server_default=sa.text("NOW()"),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.CheckConstraint(
            "verification_status IN ('pending','approved','rejected','verified','disputed')",
            name="ck_streets_verification_status",
        ),
        sa.ForeignKeyConstraint(
            ["enumerator_id"], ["users.id"], name="fk_streets_enumerator_id"
        ),
        sa.ForeignKeyConstraint(
            ["reviewed_by"], ["users.id"], name="fk_streets_reviewed_by"
        ),
        sa.PrimaryKeyConstraint("id", name="streets_pkey"),
        sa.UniqueConstraint("street_id", name="uq_streets_street_id"),
    )
    # Replace placeholder geom column with proper PostGIS geometry type
    op.execute("ALTER TABLE streets DROP COLUMN geom")
    op.execute(
        "ALTER TABLE streets ADD COLUMN geom GEOMETRY(LineString, 4326) NOT NULL"
    )
    op.execute("CREATE INDEX idx_streets_geom ON streets USING GIST(geom)")
    op.create_index("idx_streets_lga", "streets", ["lga"])
    op.create_index("idx_streets_status", "streets", ["verification_status"])
    op.create_index("idx_streets_enumerator", "streets", ["enumerator_id"])

    # ── buildings ─────────────────────────────────────────────────────────────
    op.create_table(
        "buildings",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("building_id", sa.Text(), nullable=False),
        sa.Column("street_id", sa.Text(), nullable=False),
        sa.Column("building_type", sa.Text(), nullable=False),
        sa.Column("number_of_floors", sa.Integer(), nullable=False),
        sa.Column("number_of_units", sa.Integer(), nullable=False),
        sa.Column("building_condition", sa.Text(), nullable=False),
        sa.Column("has_signage", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("business_names", postgresql.ARRAY(sa.Text()), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column(
            "geom",
            sa.Text(),  # placeholder; actual type set via raw SQL below
            nullable=False,
        ),
        sa.Column("gps_accuracy_m", sa.Numeric(8, 3), nullable=False),
        sa.Column("zone", sa.Text(), nullable=True),
        sa.Column("lga", sa.Text(), nullable=False),
        sa.Column("ward", sa.Text(), nullable=True),
        sa.Column("postcode", sa.Text(), nullable=True),
        sa.Column(
            "postcode_status", sa.Text(), nullable=False, server_default="resolved"
        ),
        sa.Column("enumerator_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("enumeration_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "verification_status",
            sa.Text(),
            nullable=False,
            server_default="pending",
        ),
        sa.Column("reviewed_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("rejection_reason", sa.Text(), nullable=True),
        sa.Column("dispute_reason", sa.Text(), nullable=True),
        sa.Column("verified_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("verified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("boundary_flag", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column(
            "gps_accuracy_flag", sa.Boolean(), nullable=False, server_default="false"
        ),
        sa.Column(
            "duplicate_flag", sa.Boolean(), nullable=False, server_default="false"
        ),
        sa.Column("qa_flags", postgresql.JSONB(), nullable=True),
        sa.Column("qr_code_value", sa.Text(), nullable=True),
        sa.Column("device_local_id", sa.Integer(), nullable=True),
        sa.Column("device_id", sa.Text(), nullable=True),
        sa.Column(
            "synced_at",
            sa.DateTime(timezone=True),
            nullable=True,
            server_default=sa.text("NOW()"),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.CheckConstraint(
            "verification_status IN ('pending','approved','rejected','verified','disputed')",
            name="ck_buildings_verification_status",
        ),
        sa.CheckConstraint(
            "postcode_status IN ('resolved','unresolved')",
            name="ck_buildings_postcode_status",
        ),
        sa.ForeignKeyConstraint(
            ["street_id"], ["streets.street_id"], name="fk_buildings_street_id"
        ),
        sa.ForeignKeyConstraint(
            ["enumerator_id"], ["users.id"], name="fk_buildings_enumerator_id"
        ),
        sa.ForeignKeyConstraint(
            ["reviewed_by"], ["users.id"], name="fk_buildings_reviewed_by"
        ),
        sa.ForeignKeyConstraint(
            ["verified_by"], ["users.id"], name="fk_buildings_verified_by"
        ),
        sa.PrimaryKeyConstraint("id", name="buildings_pkey"),
        sa.UniqueConstraint("building_id", name="uq_buildings_building_id"),
        sa.UniqueConstraint("qr_code_value", name="uq_buildings_qr_code_value"),
    )
    # Replace placeholder geom column with proper PostGIS geometry type
    op.execute("ALTER TABLE buildings DROP COLUMN geom")
    op.execute("ALTER TABLE buildings ADD COLUMN geom GEOMETRY(Point, 4326) NOT NULL")
    op.execute("CREATE INDEX idx_buildings_geom ON buildings USING GIST(geom)")
    op.create_index("idx_buildings_lga", "buildings", ["lga"])
    op.create_index("idx_buildings_street", "buildings", ["street_id"])
    op.create_index("idx_buildings_status", "buildings", ["verification_status"])
    op.create_index("idx_buildings_enumerator", "buildings", ["enumerator_id"])

    # ── photos ────────────────────────────────────────────────────────────────
    op.create_table(
        "photos",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("photo_id", sa.Text(), nullable=False),
        sa.Column("record_type", sa.Text(), nullable=False),
        sa.Column("record_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("storage_path", sa.Text(), nullable=False),
        sa.Column("is_frontage", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column(
            "geom",
            sa.Text(),  # placeholder; actual type set via raw SQL below
            nullable=True,
        ),
        sa.Column("captured_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("file_size_bytes", sa.Integer(), nullable=True),
        sa.Column(
            "synced_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.CheckConstraint(
            "record_type IN ('street','building')",
            name="ck_photos_record_type",
        ),
        sa.PrimaryKeyConstraint("id", name="photos_pkey"),
        sa.UniqueConstraint("photo_id", name="uq_photos_photo_id"),
    )
    # Replace placeholder geom column with proper PostGIS geometry type
    op.execute("ALTER TABLE photos DROP COLUMN geom")
    op.execute("ALTER TABLE photos ADD COLUMN geom GEOMETRY(Point, 4326)")
    op.create_index("idx_photos_record", "photos", ["record_type", "record_id"])

    # ── audit_log ─────────────────────────────────────────────────────────────
    op.create_table(
        "audit_log",
        sa.Column(
            "id", sa.BigInteger(), autoincrement=True, nullable=False
        ),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("operation", sa.Text(), nullable=False),
        sa.Column("entity_type", sa.Text(), nullable=True),
        sa.Column("entity_id", sa.Text(), nullable=True),
        sa.Column("detail", postgresql.JSONB(), nullable=True),
        sa.Column("ip_address", postgresql.INET(), nullable=True),
        sa.Column(
            "occurred_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], name="fk_audit_log_user_id"
        ),
        sa.PrimaryKeyConstraint("id", name="audit_log_pkey"),
    )

    # Immutability trigger function and triggers
    op.execute(
        """
        CREATE OR REPLACE FUNCTION audit_log_immutable() RETURNS TRIGGER AS $$
        BEGIN
            RAISE EXCEPTION 'audit_log is immutable: updates and deletes are not permitted';
        END;
        $$ LANGUAGE plpgsql
        """
    )
    op.execute(
        """
        CREATE TRIGGER trg_audit_log_no_update
            BEFORE UPDATE ON audit_log
            FOR EACH ROW EXECUTE FUNCTION audit_log_immutable()
        """
    )
    op.execute(
        """
        CREATE TRIGGER trg_audit_log_no_delete
            BEFORE DELETE ON audit_log
            FOR EACH ROW EXECUTE FUNCTION audit_log_immutable()
        """
    )

    # ── sync_sessions ─────────────────────────────────────────────────────────
    op.create_table(
        "sync_sessions",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("device_id", sa.Text(), nullable=False),
        sa.Column(
            "started_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "records_received", sa.Integer(), nullable=False, server_default="0"
        ),
        sa.Column(
            "records_accepted", sa.Integer(), nullable=False, server_default="0"
        ),
        sa.Column(
            "records_rejected", sa.Integer(), nullable=False, server_default="0"
        ),
        sa.Column(
            "status", sa.Text(), nullable=False, server_default="in_progress"
        ),
        sa.CheckConstraint(
            "status IN ('in_progress','completed','failed')",
            name="ck_sync_sessions_status",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], name="fk_sync_sessions_user_id"
        ),
        sa.PrimaryKeyConstraint("id", name="sync_sessions_pkey"),
    )


def downgrade() -> None:
    op.drop_table("sync_sessions")

    # Drop triggers and function before dropping audit_log
    op.execute("DROP TRIGGER IF EXISTS trg_audit_log_no_delete ON audit_log")
    op.execute("DROP TRIGGER IF EXISTS trg_audit_log_no_update ON audit_log")
    op.execute("DROP FUNCTION IF EXISTS audit_log_immutable()")

    op.drop_table("audit_log")
    op.drop_index("idx_photos_record", table_name="photos")
    op.drop_table("photos")

    op.drop_index("idx_buildings_enumerator", table_name="buildings")
    op.drop_index("idx_buildings_status", table_name="buildings")
    op.drop_index("idx_buildings_street", table_name="buildings")
    op.drop_index("idx_buildings_lga", table_name="buildings")
    op.execute("DROP INDEX IF EXISTS idx_buildings_geom")
    op.drop_table("buildings")

    op.drop_index("idx_streets_enumerator", table_name="streets")
    op.drop_index("idx_streets_status", table_name="streets")
    op.drop_index("idx_streets_lga", table_name="streets")
    op.execute("DROP INDEX IF EXISTS idx_streets_geom")
    op.drop_table("streets")

    op.drop_table("shapefile_versions")
    op.drop_table("dropdown_config")
    op.drop_index("idx_users_role", table_name="users")
    op.drop_table("users")
    op.drop_table("roles")

