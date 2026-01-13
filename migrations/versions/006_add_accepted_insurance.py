"""Add accepted insurance field to doctors

Revision ID: 006_add_accepted_insurance
Revises: 005_add_health_tracking_tables
Create Date: 2026-01-12 00:00:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector


# revision identifiers, used by Alembic.
revision = '006_add_accepted_insurance'
down_revision = '005_add_health_tracking_tables'
branch_labels = None
depends_on = None


def column_exists(table_name, column_name):
    """Check if a column exists in a table"""
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)
    columns = [col['name'] for col in inspector.get_columns(table_name)]
    return column_name in columns


def upgrade():
    if not column_exists('doctors', 'accepted_insurance'):
        op.add_column('doctors', sa.Column('accepted_insurance', sa.Text(), nullable=True))


def downgrade():
    if column_exists('doctors', 'accepted_insurance'):
        op.drop_column('doctors', 'accepted_insurance')
