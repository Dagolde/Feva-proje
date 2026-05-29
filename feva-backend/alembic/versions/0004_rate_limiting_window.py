"""Add failed_attempts_window_start for rate limiting

Revision ID: 0004
Revises: 0003
Create Date: 2025-01-XX

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0004'
down_revision = '0003'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add failed_attempts_window_start column to users table
    op.add_column('users', sa.Column('failed_attempts_window_start', sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    # Remove failed_attempts_window_start column
    op.drop_column('users', 'failed_attempts_window_start')
