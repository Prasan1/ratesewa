"""Add email verified flag

Revision ID: 003_add_email_verified
Revises: 002_review_behavior_signals
Create Date: 2026-01-09 00:40:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '003_add_email_verified'
down_revision = '002_review_behavior_signals'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('users', sa.Column('email_verified', sa.Boolean(), nullable=True))
    op.execute("UPDATE users SET email_verified = 1 WHERE email_verified IS NULL")


def downgrade():
    op.drop_column('users', 'email_verified')
