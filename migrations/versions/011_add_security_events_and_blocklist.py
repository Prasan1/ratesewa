"""Add security events and blocklist tables

Revision ID: 011_security_events_blocklist
Revises: 010_user_verify_sent
Create Date: 2026-02-01 00:00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '011_security_events_blocklist'
down_revision = '010_user_verify_sent'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'blocked_identities',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('block_type', sa.String(length=20), nullable=False),
        sa.Column('value', sa.String(length=255), nullable=False),
        sa.Column('reason', sa.Text(), nullable=True),
        sa.Column('active', sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column('created_by', sa.Integer(), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index('ix_blocked_identities_type_value', 'blocked_identities', ['block_type', 'value'])

    op.create_table(
        'security_events',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('event_type', sa.String(length=50), nullable=False),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('email', sa.String(length=200), nullable=True),
        sa.Column('ip', sa.String(length=64), nullable=True),
        sa.Column('user_agent', sa.String(length=255), nullable=True),
        sa.Column('path', sa.String(length=255), nullable=True),
        sa.Column('method', sa.String(length=10), nullable=True),
        sa.Column('meta', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index('ix_security_events_created_at', 'security_events', ['created_at'])


def downgrade():
    op.drop_index('ix_security_events_created_at', table_name='security_events')
    op.drop_table('security_events')
    op.drop_index('ix_blocked_identities_type_value', table_name='blocked_identities')
    op.drop_table('blocked_identities')
