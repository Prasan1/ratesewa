"""Add normalized doctor tables

Revision ID: 001_add_normalized
Revises:
Create Date: 2026-01-08 22:20:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '001_add_normalized'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create doctor_contact table
    op.create_table('doctor_contact',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('doctor_id', sa.Integer(), nullable=False),
        sa.Column('phone_number', sa.String(length=20), nullable=True),
        sa.Column('practice_address', sa.Text(), nullable=True),
        sa.Column('workplace', sa.Text(), nullable=True),
        sa.Column('latitude', sa.Float(), nullable=True),
        sa.Column('longitude', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['doctor_id'], ['doctors.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('doctor_id')
    )

    # Create doctor_subscription table
    op.create_table('doctor_subscription',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('doctor_id', sa.Integer(), nullable=False),
        sa.Column('subscription_tier', sa.String(length=20), nullable=True),
        sa.Column('subscription_expires_at', sa.DateTime(), nullable=True),
        sa.Column('trial_ends_at', sa.DateTime(), nullable=True),
        sa.Column('stripe_customer_id', sa.String(length=255), nullable=True),
        sa.Column('profile_views', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['doctor_id'], ['doctors.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('doctor_id')
    )

    # Create doctor_credentials table
    op.create_table('doctor_credentials',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('doctor_id', sa.Integer(), nullable=False),
        sa.Column('nmc_number', sa.String(length=50), nullable=True),
        sa.Column('external_clinic_url', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['doctor_id'], ['doctors.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('doctor_id')
    )

    # Create doctor_settings table
    op.create_table('doctor_settings',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('doctor_id', sa.Integer(), nullable=False),
        sa.Column('photo_url', sa.Text(), nullable=True),
        sa.Column('working_hours', sa.Text(), nullable=True),
        sa.Column('clinic_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['clinic_id'], ['clinics.id'], ),
        sa.ForeignKeyConstraint(['doctor_id'], ['doctors.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('doctor_id')
    )

    # Create doctor_medical_tools table
    op.create_table('doctor_medical_tools',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('doctor_id', sa.Integer(), nullable=False),
        sa.Column('signature_image', sa.Text(), nullable=True),
        sa.Column('clinic_letterhead', sa.Text(), nullable=True),
        sa.Column('default_clinic_name', sa.String(length=255), nullable=True),
        sa.Column('default_clinic_address', sa.Text(), nullable=True),
        sa.Column('default_consultation_fee', sa.Integer(), nullable=True),
        sa.Column('certificate_settings', sa.Text(), nullable=True),
        sa.Column('prescription_settings', sa.Text(), nullable=True),
        sa.Column('tools_enabled', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['doctor_id'], ['doctors.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('doctor_id')
    )

    # Create doctor_template_usage table
    op.create_table('doctor_template_usage',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('doctor_id', sa.Integer(), nullable=False),
        sa.Column('template_type', sa.String(length=50), nullable=True),
        sa.Column('generated_at', sa.DateTime(), nullable=True),
        sa.Column('patient_name', sa.String(length=100), nullable=True),
        sa.ForeignKeyConstraint(['doctor_id'], ['doctors.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Note: Data migration is handled separately in migrations/data_migration.py
    # Run that script after this migration to copy data from doctors table


def downgrade():
    op.drop_table('doctor_template_usage')
    op.drop_table('doctor_medical_tools')
    op.drop_table('doctor_settings')
    op.drop_table('doctor_credentials')
    op.drop_table('doctor_subscription')
    op.drop_table('doctor_contact')
