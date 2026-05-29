"""Add export_tasks table

Revision ID: 0005
Revises: 0004
Create Date: 2025-01-XX

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0005'
down_revision = '0004'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create export_tasks table
    op.create_table(
        'export_tasks',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('format', sa.Text(), nullable=False),
        sa.Column('entity_type', sa.Text(), nullable=False),
        sa.Column('filters', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('status', sa.Text(), server_default='pending', nullable=False),
        sa.Column('file_path', sa.Text(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index('idx_export_tasks_created_by', 'export_tasks', ['created_by'])
    op.create_index('idx_export_tasks_status', 'export_tasks', ['status'])
    op.create_index('idx_export_tasks_created_at', 'export_tasks', ['created_at'], postgresql_ops={'created_at': 'DESC'})


def downgrade() -> None:
    # Drop indexes
    op.drop_index('idx_export_tasks_created_at', table_name='export_tasks')
    op.drop_index('idx_export_tasks_status', table_name='export_tasks')
    op.drop_index('idx_export_tasks_created_by', table_name='export_tasks')
    
    # Drop table
    op.drop_table('export_tasks')
