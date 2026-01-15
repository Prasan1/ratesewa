"""Add created_at timestamp to doctors for ranking score

Revision ID: 009_add_doctor_created_at
Revises: 008_add_article_quick_answer
Create Date: 2026-01-14 00:00:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector


# revision identifiers, used by Alembic.
revision = '009_add_doctor_created_at'
down_revision = '008_add_article_quick_answer'
branch_labels = None
depends_on = None


def column_exists(table_name, column_name):
    """Check if a column exists in a table"""
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)
    columns = [col['name'] for col in inspector.get_columns(table_name)]
    return column_name in columns


def upgrade():
    if not column_exists('doctors', 'created_at'):
        op.add_column('doctors', sa.Column('created_at', sa.DateTime(), nullable=True))
        # Set existing doctors to current timestamp
        op.execute("UPDATE doctors SET created_at = CURRENT_TIMESTAMP WHERE created_at IS NULL")


def downgrade():
    if column_exists('doctors', 'created_at'):
        op.drop_column('doctors', 'created_at')
