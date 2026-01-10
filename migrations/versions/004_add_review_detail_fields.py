"""Add structured review detail fields

Revision ID: 004_add_review_detail_fields
Revises: 003_add_email_verified
Create Date: 2026-01-09 01:15:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '004_add_review_detail_fields'
down_revision = '003_add_email_verified'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('ratings', sa.Column('visit_type', sa.String(length=20), nullable=True))
    op.add_column('ratings', sa.Column('visit_reason', sa.String(length=255), nullable=True))
    op.add_column('ratings', sa.Column('recommendation', sa.String(length=5), nullable=True))
    op.add_column('ratings', sa.Column('value_rating', sa.Integer(), nullable=True))
    op.add_column('ratings', sa.Column('bedside_rating', sa.Integer(), nullable=True))
    op.add_column('ratings', sa.Column('cleanliness_rating', sa.Integer(), nullable=True))


def downgrade():
    op.drop_column('ratings', 'cleanliness_rating')
    op.drop_column('ratings', 'bedside_rating')
    op.drop_column('ratings', 'value_rating')
    op.drop_column('ratings', 'recommendation')
    op.drop_column('ratings', 'visit_reason')
    op.drop_column('ratings', 'visit_type')
