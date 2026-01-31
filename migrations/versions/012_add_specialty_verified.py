"""Add specialty_verified field to doctors

Revision ID: 012_add_specialty_verified
Revises: 011_add_security_events_and_blocklist
Create Date: 2026-01-30 00:00:00

This field tracks whether a claimed doctor's specialty has been verified by admin.
Only matters for claimed-but-unverified doctors (is_verified=False).
Verified doctors already have all their info confirmed, so this field is ignored for them.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector


revision = '012_add_specialty_verified'
down_revision = '011_security_events_blocklist'
branch_labels = None
depends_on = None


def column_exists(table_name, column_name):
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)
    columns = [col['name'] for col in inspector.get_columns(table_name)]
    return column_name in columns


def upgrade():
    if not column_exists('doctors', 'specialty_verified'):
        op.add_column('doctors', sa.Column('specialty_verified', sa.Boolean(), nullable=True))


def downgrade():
    if column_exists('doctors', 'specialty_verified'):
        op.drop_column('doctors', 'specialty_verified')
