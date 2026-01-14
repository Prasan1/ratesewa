#!/usr/bin/env python3
"""
Create all missing clinic-related tables in production database.
This fixes the 500 errors caused by missing clinic_doctors and related tables.

Tables created (in order):
1. clinics
2. clinic_manager_doctors
3. clinic_accounts
4. clinic_staff
5. clinic_doctors
6. clinic_schedules
7. schedule_exceptions
8. appointment_reminders
9. patient_no_show_records
"""

import os
import sys
from sqlalchemy import create_engine, text, inspect

# Database URL from environment
DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///instance/doctors.db')

# Fix postgres:// to postgresql://
if DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

print("=" * 60)
print("CREATING MISSING CLINIC TABLES IN PRODUCTION DATABASE")
print("=" * 60)
print(f"Database: {DATABASE_URL.split('@')[-1] if '@' in DATABASE_URL else DATABASE_URL}\n")

engine = create_engine(DATABASE_URL)

# Define table creation SQL statements (in order of dependencies)
TABLE_DEFINITIONS = {
    'clinics': """
        CREATE TABLE IF NOT EXISTS clinics (
            id SERIAL PRIMARY KEY,
            name VARCHAR(200) NOT NULL,
            slug VARCHAR(250) UNIQUE NOT NULL,
            city_id INTEGER REFERENCES cities(id),
            address TEXT,
            city VARCHAR(100),
            phone_number VARCHAR(20),
            phone VARCHAR(20),
            email VARCHAR(120),
            website VARCHAR(200),
            description TEXT,
            logo_url VARCHAR(500),
            clinic_type VARCHAR(50) DEFAULT 'clinic',
            is_featured BOOLEAN DEFAULT FALSE,
            is_active BOOLEAN DEFAULT TRUE,
            is_verified BOOLEAN DEFAULT FALSE,
            created_by_user_id INTEGER REFERENCES users(id),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """,

    'clinic_manager_doctors': """
        CREATE TABLE IF NOT EXISTS clinic_manager_doctors (
            id SERIAL PRIMARY KEY,
            manager_user_id INTEGER NOT NULL REFERENCES users(id),
            doctor_id INTEGER NOT NULL REFERENCES doctors(id),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """,

    'clinic_accounts': """
        CREATE TABLE IF NOT EXISTS clinic_accounts (
            id SERIAL PRIMARY KEY,
            manager_user_id INTEGER NOT NULL REFERENCES users(id),
            name VARCHAR(200),
            subscription_tier VARCHAR(50) DEFAULT 'clinic_starter',
            max_doctors INTEGER DEFAULT 3,
            subscription_expires_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """,

    'clinic_staff': """
        CREATE TABLE IF NOT EXISTS clinic_staff (
            id SERIAL PRIMARY KEY,
            clinic_id INTEGER NOT NULL REFERENCES clinics(id),
            user_id INTEGER NOT NULL REFERENCES users(id),
            role VARCHAR(50) DEFAULT 'staff',
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            CONSTRAINT unique_clinic_staff UNIQUE (clinic_id, user_id)
        )
    """,

    'clinic_doctors': """
        CREATE TABLE IF NOT EXISTS clinic_doctors (
            id SERIAL PRIMARY KEY,
            clinic_id INTEGER NOT NULL REFERENCES clinics(id),
            doctor_id INTEGER NOT NULL REFERENCES doctors(id),
            role VARCHAR(50) DEFAULT 'consultant',
            consultation_fee INTEGER,
            status VARCHAR(20) DEFAULT 'pending',
            invited_by_user_id INTEGER REFERENCES users(id),
            responded_at TIMESTAMP,
            rejection_reason VARCHAR(500),
            slot_duration_minutes INTEGER DEFAULT 15,
            max_patients_per_slot INTEGER DEFAULT 1,
            accepts_online_booking BOOLEAN DEFAULT TRUE,
            booking_notice_hours INTEGER DEFAULT 2,
            cancellation_notice_hours INTEGER DEFAULT 24,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            CONSTRAINT unique_clinic_doctor UNIQUE (clinic_id, doctor_id)
        )
    """,

    'clinic_schedules': """
        CREATE TABLE IF NOT EXISTS clinic_schedules (
            id SERIAL PRIMARY KEY,
            clinic_doctor_id INTEGER NOT NULL REFERENCES clinic_doctors(id),
            day_of_week INTEGER NOT NULL,
            start_time TIME NOT NULL,
            end_time TIME NOT NULL,
            max_appointments INTEGER DEFAULT 20,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """,

    'schedule_exceptions': """
        CREATE TABLE IF NOT EXISTS schedule_exceptions (
            id SERIAL PRIMARY KEY,
            clinic_doctor_id INTEGER NOT NULL REFERENCES clinic_doctors(id),
            exception_date DATE NOT NULL,
            exception_type VARCHAR(20) NOT NULL,
            start_time TIME,
            end_time TIME,
            reason VARCHAR(200),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """,

    'appointment_reminders': """
        CREATE TABLE IF NOT EXISTS appointment_reminders (
            id SERIAL PRIMARY KEY,
            appointment_id INTEGER NOT NULL REFERENCES appointments(id),
            reminder_type VARCHAR(20) NOT NULL,
            sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status VARCHAR(20) DEFAULT 'sent',
            response_received BOOLEAN DEFAULT FALSE,
            response_text VARCHAR(200),
            response_at TIMESTAMP
        )
    """,

    'patient_no_show_records': """
        CREATE TABLE IF NOT EXISTS patient_no_show_records (
            id SERIAL PRIMARY KEY,
            patient_phone VARCHAR(20) NOT NULL,
            patient_user_id INTEGER REFERENCES users(id),
            appointment_id INTEGER NOT NULL REFERENCES appointments(id),
            no_show_date DATE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """
}

# Index definitions
INDEX_DEFINITIONS = [
    ("idx_clinics_slug", "CREATE INDEX IF NOT EXISTS idx_clinics_slug ON clinics(slug)"),
    ("idx_clinic_doctors_doctor", "CREATE INDEX IF NOT EXISTS idx_clinic_doctors_doctor ON clinic_doctors(doctor_id)"),
    ("idx_clinic_doctors_clinic", "CREATE INDEX IF NOT EXISTS idx_clinic_doctors_clinic ON clinic_doctors(clinic_id)"),
    ("idx_clinic_doctors_status", "CREATE INDEX IF NOT EXISTS idx_clinic_doctors_status ON clinic_doctors(status)"),
    ("idx_clinic_schedules_doctor", "CREATE INDEX IF NOT EXISTS idx_clinic_schedules_doctor ON clinic_schedules(clinic_doctor_id)"),
    ("idx_patient_no_show_phone", "CREATE INDEX IF NOT EXISTS idx_patient_no_show_phone ON patient_no_show_records(patient_phone)"),
]

tables_created = 0
tables_existed = 0
errors = 0

try:
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()
    print(f"Found {len(existing_tables)} existing tables in database\n")

    # Create tables in order
    for table_name, create_sql in TABLE_DEFINITIONS.items():
        print(f"Processing table: {table_name}")

        if table_name in existing_tables:
            print(f"  Already exists")
            tables_existed += 1
            continue

        try:
            with engine.connect() as conn:
                trans = conn.begin()
                conn.execute(text(create_sql))
                trans.commit()
            print(f"  Created successfully")
            tables_created += 1
        except Exception as e:
            error_msg = str(e).lower()
            if "already exists" in error_msg:
                print(f"  Already exists (concurrent creation)")
                tables_existed += 1
            else:
                print(f"  ERROR: {e}")
                errors += 1

    # Create indexes
    print(f"\n{'=' * 60}")
    print("CREATING INDEXES")
    print(f"{'=' * 60}")

    for idx_name, idx_sql in INDEX_DEFINITIONS:
        try:
            with engine.connect() as conn:
                trans = conn.begin()
                conn.execute(text(idx_sql))
                trans.commit()
            print(f"  {idx_name}: OK")
        except Exception as e:
            error_msg = str(e).lower()
            if "already exists" in error_msg:
                print(f"  {idx_name}: already exists")
            else:
                print(f"  {idx_name}: ERROR - {e}")

    # Summary
    print(f"\n{'=' * 60}")
    print("MIGRATION COMPLETED!")
    print(f"{'=' * 60}")
    print(f"Tables created: {tables_created}")
    print(f"Tables already existed: {tables_existed}")
    print(f"Errors: {errors}")

    if errors > 0:
        print("\nSome tables failed to create. Review errors above.")
        sys.exit(1)
    else:
        print("\nAll clinic tables are now available!")

except Exception as e:
    print(f"\nMIGRATION FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
