"""Add clinic and appointment system tables

Revision ID: 007_add_clinic_appointment_tables
Revises: 006_add_accepted_insurance
Create Date: 2026-01-12 00:00:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector


# revision identifiers, used by Alembic.
revision = '007_add_clinic_appointment_tables'
down_revision = '006_add_accepted_insurance'
branch_labels = None
depends_on = None


def table_exists(table_name):
    """Check if a table exists in the database"""
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)
    return table_name in inspector.get_table_names()


def column_exists(table_name, column_name):
    """Check if a column exists in a table"""
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)
    columns = [col['name'] for col in inspector.get_columns(table_name)]
    return column_name in columns


def upgrade():
    # ==== Update existing clinics table with new columns ====
    if table_exists('clinics'):
        # Add new columns to existing clinics table if they don't exist
        if not column_exists('clinics', 'city'):
            op.add_column('clinics', sa.Column('city', sa.String(100), nullable=True))
        if not column_exists('clinics', 'phone'):
            op.add_column('clinics', sa.Column('phone', sa.String(20), nullable=True))
        if not column_exists('clinics', 'email'):
            op.add_column('clinics', sa.Column('email', sa.String(120), nullable=True))
        if not column_exists('clinics', 'website'):
            op.add_column('clinics', sa.Column('website', sa.String(200), nullable=True))
        if not column_exists('clinics', 'clinic_type'):
            op.add_column('clinics', sa.Column('clinic_type', sa.String(50), nullable=True, server_default='clinic'))
        if not column_exists('clinics', 'logo_url'):
            op.add_column('clinics', sa.Column('logo_url', sa.String(500), nullable=True))
        if not column_exists('clinics', 'created_by_user_id'):
            op.add_column('clinics', sa.Column('created_by_user_id', sa.Integer(), nullable=True))
            # Can't add FK constraint if column might have NULL values for existing rows
        if not column_exists('clinics', 'is_verified'):
            op.add_column('clinics', sa.Column('is_verified', sa.Boolean(), server_default='0'))
        if not column_exists('clinics', 'created_at'):
            op.add_column('clinics', sa.Column('created_at', sa.DateTime(), nullable=True))
        if not column_exists('clinics', 'updated_at'):
            op.add_column('clinics', sa.Column('updated_at', sa.DateTime(), nullable=True))
    else:
        # Create clinics table if it doesn't exist
        op.create_table('clinics',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('name', sa.String(200), nullable=False),
            sa.Column('slug', sa.String(250), nullable=False),
            sa.Column('city_id', sa.Integer(), nullable=True),
            sa.Column('address', sa.Text(), nullable=True),
            sa.Column('city', sa.String(100), nullable=True),
            sa.Column('phone_number', sa.String(20), nullable=True),
            sa.Column('phone', sa.String(20), nullable=True),
            sa.Column('email', sa.String(120), nullable=True),
            sa.Column('website', sa.String(200), nullable=True),
            sa.Column('description', sa.Text(), nullable=True),
            sa.Column('logo_url', sa.String(500), nullable=True),
            sa.Column('clinic_type', sa.String(50), nullable=True, server_default='clinic'),
            sa.Column('is_featured', sa.Boolean(), server_default='0'),
            sa.Column('is_active', sa.Boolean(), server_default='1'),
            sa.Column('is_verified', sa.Boolean(), server_default='0'),
            sa.Column('created_by_user_id', sa.Integer(), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.Column('updated_at', sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(['city_id'], ['cities.id'], ),
            sa.ForeignKeyConstraint(['created_by_user_id'], ['users.id'], ),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('slug')
        )
        op.create_index('idx_clinic_slug', 'clinics', ['slug'])

    # ==== Update existing appointments table with new columns ====
    if table_exists('appointments'):
        # Add new columns to existing appointments table
        if not column_exists('appointments', 'clinic_doctor_id'):
            op.add_column('appointments', sa.Column('clinic_doctor_id', sa.Integer(), nullable=True))
        if not column_exists('appointments', 'patient_name'):
            op.add_column('appointments', sa.Column('patient_name', sa.String(200), nullable=True))
        if not column_exists('appointments', 'patient_phone'):
            op.add_column('appointments', sa.Column('patient_phone', sa.String(20), nullable=True))
        if not column_exists('appointments', 'patient_email'):
            op.add_column('appointments', sa.Column('patient_email', sa.String(120), nullable=True))
        if not column_exists('appointments', 'patient_user_id'):
            op.add_column('appointments', sa.Column('patient_user_id', sa.Integer(), nullable=True))
        if not column_exists('appointments', 'reason'):
            op.add_column('appointments', sa.Column('reason', sa.Text(), nullable=True))
        if not column_exists('appointments', 'booking_code'):
            op.add_column('appointments', sa.Column('booking_code', sa.String(10), nullable=True))
        if not column_exists('appointments', 'queue_position'):
            op.add_column('appointments', sa.Column('queue_position', sa.Integer(), nullable=True))
        if not column_exists('appointments', 'notes'):
            op.add_column('appointments', sa.Column('notes', sa.Text(), nullable=True))
        if not column_exists('appointments', 'confirmation_sent_at'):
            op.add_column('appointments', sa.Column('confirmation_sent_at', sa.DateTime(), nullable=True))
        if not column_exists('appointments', 'confirmed_at'):
            op.add_column('appointments', sa.Column('confirmed_at', sa.DateTime(), nullable=True))
        if not column_exists('appointments', 'checked_in_at'):
            op.add_column('appointments', sa.Column('checked_in_at', sa.DateTime(), nullable=True))
        if not column_exists('appointments', 'completed_at'):
            op.add_column('appointments', sa.Column('completed_at', sa.DateTime(), nullable=True))
        if not column_exists('appointments', 'cancelled_at'):
            op.add_column('appointments', sa.Column('cancelled_at', sa.DateTime(), nullable=True))
        if not column_exists('appointments', 'cancellation_reason'):
            op.add_column('appointments', sa.Column('cancellation_reason', sa.String(500), nullable=True))
        if not column_exists('appointments', 'updated_at'):
            op.add_column('appointments', sa.Column('updated_at', sa.DateTime(), nullable=True))

        # Create indexes if they don't exist (will fail silently if they exist)
        try:
            op.create_index('idx_appointment_booking_code', 'appointments', ['booking_code'])
        except:
            pass
        try:
            op.create_index('idx_appointment_patient_phone', 'appointments', ['patient_phone'])
        except:
            pass
    else:
        # Create appointments table if it doesn't exist
        op.create_table('appointments',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('doctor_id', sa.Integer(), nullable=True),
            sa.Column('user_id', sa.Integer(), nullable=True),
            sa.Column('message', sa.Text(), nullable=True),
            sa.Column('clinic_doctor_id', sa.Integer(), nullable=True),
            sa.Column('appointment_date', sa.Date(), nullable=True),
            sa.Column('appointment_time', sa.Time(), nullable=True),
            sa.Column('patient_name', sa.String(200), nullable=True),
            sa.Column('patient_phone', sa.String(20), nullable=True),
            sa.Column('patient_email', sa.String(120), nullable=True),
            sa.Column('patient_user_id', sa.Integer(), nullable=True),
            sa.Column('reason', sa.Text(), nullable=True),
            sa.Column('booking_code', sa.String(10), nullable=True),
            sa.Column('status', sa.String(50), nullable=True, server_default='pending'),
            sa.Column('queue_position', sa.Integer(), nullable=True),
            sa.Column('notes', sa.Text(), nullable=True),
            sa.Column('confirmation_sent_at', sa.DateTime(), nullable=True),
            sa.Column('confirmed_at', sa.DateTime(), nullable=True),
            sa.Column('checked_in_at', sa.DateTime(), nullable=True),
            sa.Column('completed_at', sa.DateTime(), nullable=True),
            sa.Column('cancelled_at', sa.DateTime(), nullable=True),
            sa.Column('cancellation_reason', sa.String(500), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.Column('updated_at', sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(['doctor_id'], ['doctors.id'], ),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
            sa.ForeignKeyConstraint(['patient_user_id'], ['users.id'], ),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index('idx_appointment_booking_code', 'appointments', ['booking_code'])
        op.create_index('idx_appointment_patient_phone', 'appointments', ['patient_phone'])

    # ==== Create new tables ====

    # Clinic Staff table
    if not table_exists('clinic_staff'):
        op.create_table('clinic_staff',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('clinic_id', sa.Integer(), nullable=False),
            sa.Column('user_id', sa.Integer(), nullable=False),
            sa.Column('role', sa.String(50), nullable=True, server_default='staff'),
            sa.Column('is_active', sa.Boolean(), server_default='1'),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(['clinic_id'], ['clinics.id'], ),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('clinic_id', 'user_id', name='unique_clinic_staff')
        )

    # Clinic Doctors table (links doctors to clinics)
    if not table_exists('clinic_doctors'):
        op.create_table('clinic_doctors',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('clinic_id', sa.Integer(), nullable=False),
            sa.Column('doctor_id', sa.Integer(), nullable=False),
            sa.Column('role', sa.String(50), nullable=True, server_default='consultant'),
            sa.Column('consultation_fee', sa.Integer(), nullable=True),
            sa.Column('status', sa.String(20), nullable=True, server_default='pending'),
            sa.Column('invited_by_user_id', sa.Integer(), nullable=True),
            sa.Column('responded_at', sa.DateTime(), nullable=True),
            sa.Column('rejection_reason', sa.String(500), nullable=True),
            sa.Column('slot_duration_minutes', sa.Integer(), nullable=True, server_default='15'),
            sa.Column('max_patients_per_slot', sa.Integer(), nullable=True, server_default='1'),
            sa.Column('accepts_online_booking', sa.Boolean(), server_default='1'),
            sa.Column('booking_notice_hours', sa.Integer(), nullable=True, server_default='2'),
            sa.Column('cancellation_notice_hours', sa.Integer(), nullable=True, server_default='24'),
            sa.Column('is_active', sa.Boolean(), server_default='1'),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.Column('updated_at', sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(['clinic_id'], ['clinics.id'], ),
            sa.ForeignKeyConstraint(['doctor_id'], ['doctors.id'], ),
            sa.ForeignKeyConstraint(['invited_by_user_id'], ['users.id'], ),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('clinic_id', 'doctor_id', name='unique_clinic_doctor')
        )
        op.create_index('idx_clinic_doctor_status', 'clinic_doctors', ['status'])

    # Clinic Schedules table
    if not table_exists('clinic_schedules'):
        op.create_table('clinic_schedules',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('clinic_doctor_id', sa.Integer(), nullable=False),
            sa.Column('day_of_week', sa.Integer(), nullable=False),
            sa.Column('start_time', sa.Time(), nullable=False),
            sa.Column('end_time', sa.Time(), nullable=False),
            sa.Column('max_appointments', sa.Integer(), nullable=True, server_default='20'),
            sa.Column('is_active', sa.Boolean(), server_default='1'),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(['clinic_doctor_id'], ['clinic_doctors.id'], ),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index('idx_schedule_clinic_doctor', 'clinic_schedules', ['clinic_doctor_id'])

    # Schedule Exceptions table (holidays, modified hours)
    if not table_exists('schedule_exceptions'):
        op.create_table('schedule_exceptions',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('clinic_doctor_id', sa.Integer(), nullable=False),
            sa.Column('exception_date', sa.Date(), nullable=False),
            sa.Column('exception_type', sa.String(20), nullable=False),
            sa.Column('start_time', sa.Time(), nullable=True),
            sa.Column('end_time', sa.Time(), nullable=True),
            sa.Column('reason', sa.String(200), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(['clinic_doctor_id'], ['clinic_doctors.id'], ),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index('idx_exception_date', 'schedule_exceptions', ['clinic_doctor_id', 'exception_date'])

    # Appointment Reminders table
    if not table_exists('appointment_reminders'):
        op.create_table('appointment_reminders',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('appointment_id', sa.Integer(), nullable=False),
            sa.Column('reminder_type', sa.String(20), nullable=False),
            sa.Column('sent_at', sa.DateTime(), nullable=True),
            sa.Column('status', sa.String(20), nullable=True, server_default='sent'),
            sa.Column('response_received', sa.Boolean(), server_default='0'),
            sa.Column('response_text', sa.String(200), nullable=True),
            sa.Column('response_at', sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(['appointment_id'], ['appointments.id'], ),
            sa.PrimaryKeyConstraint('id')
        )

    # Patient No-Show Records table
    if not table_exists('patient_no_show_records'):
        op.create_table('patient_no_show_records',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('patient_phone', sa.String(20), nullable=False),
            sa.Column('patient_user_id', sa.Integer(), nullable=True),
            sa.Column('appointment_id', sa.Integer(), nullable=False),
            sa.Column('clinic_id', sa.Integer(), nullable=False),
            sa.Column('no_show_date', sa.Date(), nullable=False),
            sa.Column('notes', sa.String(500), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(['patient_user_id'], ['users.id'], ),
            sa.ForeignKeyConstraint(['appointment_id'], ['appointments.id'], ),
            sa.ForeignKeyConstraint(['clinic_id'], ['clinics.id'], ),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index('idx_no_show_phone', 'patient_no_show_records', ['patient_phone'])
        op.create_index('idx_no_show_user', 'patient_no_show_records', ['patient_user_id'])


def downgrade():
    # Drop new tables
    op.drop_table('patient_no_show_records')
    op.drop_table('appointment_reminders')
    op.drop_table('schedule_exceptions')
    op.drop_table('clinic_schedules')
    op.drop_table('clinic_doctors')
    op.drop_table('clinic_staff')

    # Note: We don't drop columns from clinics/appointments since they might have existing data
    # and the original schema should still work without them
