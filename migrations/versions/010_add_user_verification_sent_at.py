"""Add last_verification_sent_at to users

Revision ID: 010_add_user_verification_sent_at
Revises: 009_add_doctor_created_at
Create Date: 2026-02-01 00:00:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector


# revision identifiers, used by Alembic.
revision = '010_add_user_verification_sent_at'
down_revision = '009_add_doctor_created_at'
branch_labels = None
depends_on = None


def column_exists(table_name, column_name):
    """Check if a column exists in a table"""
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)
    columns = [col['name'] for col in inspector.get_columns(table_name)]
    return column_name in columns


def upgrade():
    if not column_exists('users', 'last_verification_sent_at'):
        op.add_column('users', sa.Column('last_verification_sent_at', sa.DateTime(), nullable=True))


def downgrade():
    if column_exists('users', 'last_verification_sent_at'):
        op.drop_column('users', 'last_verification_sent_at')
