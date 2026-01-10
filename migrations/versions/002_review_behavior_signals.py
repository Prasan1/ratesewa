"""Add review behavior signal fields

Revision ID: 002_review_behavior_signals
Revises: 001_add_normalized
Create Date: 2026-01-09 00:20:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '002_review_behavior_signals'
down_revision = '001_add_normalized'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('users', sa.Column('created_at', sa.DateTime(), nullable=True))
    op.execute("UPDATE users SET created_at = CURRENT_TIMESTAMP WHERE created_at IS NULL")
    op.add_column('ratings', sa.Column('ip_address', sa.String(length=45), nullable=True))
    op.add_column('ratings', sa.Column('user_agent', sa.String(length=255), nullable=True))
    op.add_column('ratings', sa.Column('suspicion_score', sa.Integer(), server_default='0', nullable=True))
    op.add_column('ratings', sa.Column('is_suspected', sa.Boolean(), server_default=sa.false(), nullable=True))


def downgrade():
    op.drop_column('ratings', 'is_suspected')
    op.drop_column('ratings', 'suspicion_score')
    op.drop_column('ratings', 'user_agent')
    op.drop_column('ratings', 'ip_address')
    op.drop_column('users', 'created_at')
