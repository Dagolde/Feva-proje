"""Add completed_at column to export_tasks

Revision ID: 0007
Revises: 0006
Create Date: 2026-03-19

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0007'
down_revision = '0006'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        'export_tasks',
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True)
    )


def downgrade() -> None:
    op.drop_column('export_tasks', 'completed_at')
