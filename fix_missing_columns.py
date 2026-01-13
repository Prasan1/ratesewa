#!/usr/bin/env python3
"""
Add all missing columns to database.
Usage: python fix_missing_columns.py
"""

import os

def fix_columns():
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL not set")
        return

    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)

    import psycopg2

    print("Connecting to database...")
    conn = psycopg2.connect(database_url)
    conn.autocommit = True
    cur = conn.cursor()

    # List of columns to add: (table, column, type, default)
    columns_to_add = [
        # doctors table
        ('doctors', 'ranksewa_network_enabled', 'BOOLEAN', 'FALSE'),
        ('doctors', 'nmc_expiry_date', 'DATE', None),
        ('doctors', 'accepted_insurance', 'TEXT', None),
        ('doctors', 'trial_ends_at', 'TIMESTAMP', None),

        # articles table
        ('articles', 'quick_answer', 'TEXT', None),

        # clinics table - ALL columns from model
        ('clinics', 'city', 'VARCHAR(100)', None),
        ('clinics', 'phone_number', 'VARCHAR(20)', None),
        ('clinics', 'phone', 'VARCHAR(20)', None),
        ('clinics', 'email', 'VARCHAR(120)', None),
        ('clinics', 'website', 'VARCHAR(200)', None),
        ('clinics', 'description', 'TEXT', None),
        ('clinics', 'logo_url', 'VARCHAR(500)', None),
        ('clinics', 'clinic_type', 'VARCHAR(50)', "'clinic'"),
        ('clinics', 'is_featured', 'BOOLEAN', 'FALSE'),
        ('clinics', 'is_active', 'BOOLEAN', 'TRUE'),
        ('clinics', 'is_verified', 'BOOLEAN', 'FALSE'),
        ('clinics', 'created_by_user_id', 'INTEGER', None),
        ('clinics', 'trial_ends_at', 'TIMESTAMP', None),
        ('clinics', 'created_at', 'TIMESTAMP', 'NOW()'),
        ('clinics', 'updated_at', 'TIMESTAMP', 'NOW()'),

        # users table
        ('users', 'email_verified', 'BOOLEAN', 'FALSE'),
        ('users', 'role', 'VARCHAR(20)', "'patient'"),
        ('users', 'doctor_id', 'INTEGER', None),
        ('users', 'is_doctor_intent', 'BOOLEAN', 'FALSE'),
        ('users', 'points', 'INTEGER', '0'),

        # appointments table - new columns
        ('appointments', 'clinic_doctor_id', 'INTEGER', None),
        ('appointments', 'appointment_date', 'DATE', None),
        ('appointments', 'appointment_time', 'TIME', None),
        ('appointments', 'patient_name', 'VARCHAR(200)', None),
        ('appointments', 'patient_phone', 'VARCHAR(20)', None),
        ('appointments', 'patient_email', 'VARCHAR(120)', None),
        ('appointments', 'patient_user_id', 'INTEGER', None),
        ('appointments', 'reason', 'TEXT', None),
        ('appointments', 'booking_code', 'VARCHAR(10)', None),
        ('appointments', 'queue_position', 'INTEGER', None),
        ('appointments', 'notes', 'TEXT', None),
        ('appointments', 'confirmation_sent_at', 'TIMESTAMP', None),
        ('appointments', 'confirmed_at', 'TIMESTAMP', None),
        ('appointments', 'checked_in_at', 'TIMESTAMP', None),
        ('appointments', 'completed_at', 'TIMESTAMP', None),
        ('appointments', 'cancelled_at', 'TIMESTAMP', None),
        ('appointments', 'cancellation_reason', 'VARCHAR(500)', None),
        ('appointments', 'updated_at', 'TIMESTAMP', None),
    ]

    for table, column, col_type, default in columns_to_add:
        try:
            # Check if column exists
            cur.execute("""
                SELECT column_name FROM information_schema.columns
                WHERE table_name = %s AND column_name = %s
            """, (table, column))

            if cur.fetchone():
                print(f"✅ {table}.{column} already exists")
            else:
                print(f"Adding {table}.{column}...")
                if default:
                    cur.execute(f"ALTER TABLE {table} ADD COLUMN {column} {col_type} DEFAULT {default}")
                else:
                    cur.execute(f"ALTER TABLE {table} ADD COLUMN {column} {col_type}")
                print(f"✅ {table}.{column} added!")

        except Exception as e:
            print(f"⚠️  {table}.{column}: {e}")

    cur.close()
    conn.close()
    print("\n✅ Done!")

if __name__ == '__main__':
    fix_columns()
