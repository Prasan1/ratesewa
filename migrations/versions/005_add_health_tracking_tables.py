"""Add health tracking tables (BP, Sugar, Medications)

Revision ID: 005_add_health_tracking_tables
Revises: 004_add_review_detail_fields
Create Date: 2026-01-11 12:00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '005_add_health_tracking_tables'
down_revision = '004_add_review_detail_fields'
branch_labels = None
depends_on = None


def upgrade():
    # Blood Pressure Records
    op.create_table('bp_records',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('systolic', sa.Integer(), nullable=False),
        sa.Column('diastolic', sa.Integer(), nullable=False),
        sa.Column('pulse', sa.Integer(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_bp_records_user_id', 'bp_records', ['user_id'], unique=False)
    op.create_index('ix_bp_records_timestamp', 'bp_records', ['timestamp'], unique=False)

    # Blood Sugar Records
    op.create_table('sugar_records',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('value', sa.Integer(), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_sugar_records_user_id', 'sugar_records', ['user_id'], unique=False)
    op.create_index('ix_sugar_records_timestamp', 'sugar_records', ['timestamp'], unique=False)

    # Medications
    op.create_table('medications',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('dosage', sa.String(length=100), nullable=False),
        sa.Column('frequency', sa.String(length=100), nullable=False),
        sa.Column('instructions', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_medications_user_id', 'medications', ['user_id'], unique=False)

    # Health Consent Tracking
    op.create_table('health_consents',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('terms_version', sa.String(length=20), nullable=False),
        sa.Column('accepted_at', sa.DateTime(), nullable=False),
        sa.Column('ip_address', sa.String(length=50), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', name='unique_health_consent_user')
    )

    # Patient-Doctor Links (for health data sharing)
    op.create_table('patient_doctors',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('doctor_id', sa.Integer(), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['doctor_id'], ['doctors.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'doctor_id', name='unique_patient_doctor')
    )
    op.create_index('ix_patient_doctors_user_id', 'patient_doctors', ['user_id'], unique=False)
    op.create_index('ix_patient_doctors_doctor_id', 'patient_doctors', ['doctor_id'], unique=False)

    # Add ranksewa_network_enabled to doctors table
    op.add_column('doctors', sa.Column('ranksewa_network_enabled', sa.Boolean(), nullable=True, default=False))


def downgrade():
    op.drop_column('doctors', 'ranksewa_network_enabled')
    op.drop_index('ix_patient_doctors_doctor_id', table_name='patient_doctors')
    op.drop_index('ix_patient_doctors_user_id', table_name='patient_doctors')
    op.drop_table('patient_doctors')

    op.drop_table('health_consents')

    op.drop_index('ix_medications_user_id', table_name='medications')
    op.drop_table('medications')

    op.drop_index('ix_sugar_records_timestamp', table_name='sugar_records')
    op.drop_index('ix_sugar_records_user_id', table_name='sugar_records')
    op.drop_table('sugar_records')

    op.drop_index('ix_bp_records_timestamp', table_name='bp_records')
    op.drop_index('ix_bp_records_user_id', table_name='bp_records')
    op.drop_table('bp_records')
