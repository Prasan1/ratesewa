"""Add quick_answer field to articles

Revision ID: 008_add_article_quick_answer
Revises: 007_add_clinic_appointment_tables
Create Date: 2026-01-13

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '008_add_article_quick_answer'
down_revision = '007_add_clinic_appointment_tables'
branch_labels = None
depends_on = None


def upgrade():
    # Add quick_answer column to articles table
    op.add_column('articles', sa.Column('quick_answer', sa.Text(), nullable=True))


def downgrade():
    op.drop_column('articles', 'quick_answer')
