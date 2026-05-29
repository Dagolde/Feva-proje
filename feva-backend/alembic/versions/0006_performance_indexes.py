"""Add performance indexes for audit_log and query optimization

Revision ID: 0006
Revises: 0005
Create Date: 2025-01-XX

Requirements: 10.7
"""
from alembic import op

revision = '0006'
down_revision = '0005'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Composite index for audit log queries by entity (record audit trail lookups)
    op.create_index(
        'idx_audit_log_entity',
        'audit_log',
        ['entity_type', 'entity_id'],
    )
    # Index for audit log queries by user
    op.create_index(
        'idx_audit_log_user_occurred',
        'audit_log',
        ['user_id', 'occurred_at'],
    )
    # Composite index for export task status polling
    op.create_index(
        'idx_export_tasks_status_created',
        'export_tasks',
        ['status', 'created_at'],
    )


def downgrade() -> None:
    op.drop_index('idx_export_tasks_status_created', table_name='export_tasks')
    op.drop_index('idx_audit_log_user_occurred', table_name='audit_log')
    op.drop_index('idx_audit_log_entity', table_name='audit_log')
