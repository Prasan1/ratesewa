#!/usr/bin/env python3
"""
Create missing health tracking tables directly.
Usage: python create_missing_tables.py
"""

from app import app, db
from sqlalchemy import text, inspect

def check_table_exists(table_name):
    inspector = inspect(db.engine)
    return table_name in inspector.get_table_names()

def create_missing_tables():
    print("=" * 50)
    print("Creating missing health tracking tables...")
    print("=" * 50)

    with app.app_context():
        # Check which tables need to be created
        tables_sql = {
            'bp_records': """
                CREATE TABLE IF NOT EXISTS bp_records (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL REFERENCES users(id),
                    systolic INTEGER NOT NULL,
                    diastolic INTEGER NOT NULL,
                    pulse INTEGER,
                    notes TEXT,
                    timestamp TIMESTAMP NOT NULL,
                    created_at TIMESTAMP
                );
                CREATE INDEX IF NOT EXISTS ix_bp_records_user_id ON bp_records(user_id);
                CREATE INDEX IF NOT EXISTS ix_bp_records_timestamp ON bp_records(timestamp);
            """,
            'sugar_records': """
                CREATE TABLE IF NOT EXISTS sugar_records (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL REFERENCES users(id),
                    value INTEGER NOT NULL,
                    notes TEXT,
                    timestamp TIMESTAMP NOT NULL,
                    created_at TIMESTAMP
                );
                CREATE INDEX IF NOT EXISTS ix_sugar_records_user_id ON sugar_records(user_id);
                CREATE INDEX IF NOT EXISTS ix_sugar_records_timestamp ON sugar_records(timestamp);
            """,
            'medications': """
                CREATE TABLE IF NOT EXISTS medications (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL REFERENCES users(id),
                    name VARCHAR(200) NOT NULL,
                    dosage VARCHAR(100) NOT NULL,
                    frequency VARCHAR(100) NOT NULL,
                    instructions TEXT,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP
                );
                CREATE INDEX IF NOT EXISTS ix_medications_user_id ON medications(user_id);
            """,
            'health_consents': """
                CREATE TABLE IF NOT EXISTS health_consents (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL REFERENCES users(id),
                    terms_version VARCHAR(20) NOT NULL,
                    accepted_at TIMESTAMP NOT NULL,
                    ip_address VARCHAR(50),
                    CONSTRAINT unique_health_consent_user UNIQUE (user_id)
                );
            """,
            'patient_doctors': """
                CREATE TABLE IF NOT EXISTS patient_doctors (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL REFERENCES users(id),
                    doctor_id INTEGER NOT NULL REFERENCES doctors(id),
                    notes TEXT,
                    created_at TIMESTAMP,
                    CONSTRAINT unique_patient_doctor UNIQUE (user_id, doctor_id)
                );
                CREATE INDEX IF NOT EXISTS ix_patient_doctors_user_id ON patient_doctors(user_id);
                CREATE INDEX IF NOT EXISTS ix_patient_doctors_doctor_id ON patient_doctors(doctor_id);
            """
        }

        # Also add column to doctors if missing
        add_column_sql = """
            ALTER TABLE doctors ADD COLUMN IF NOT EXISTS ranksewa_network_enabled BOOLEAN DEFAULT FALSE;
        """

        for table_name, sql in tables_sql.items():
            if check_table_exists(table_name):
                print(f"✓ {table_name} already exists")
            else:
                print(f"Creating {table_name}...")
                try:
                    db.session.execute(text(sql))
                    db.session.commit()
                    print(f"✅ {table_name} created!")
                except Exception as e:
                    print(f"❌ Error creating {table_name}: {e}")
                    db.session.rollback()

        # Add column to doctors
        try:
            db.session.execute(text(add_column_sql))
            db.session.commit()
            print("✅ doctors.ranksewa_network_enabled column ensured")
        except Exception as e:
            print(f"Column may already exist: {e}")
            db.session.rollback()

        # Final verification
        print("\n" + "=" * 50)
        print("Verification:")
        for table_name in tables_sql.keys():
            exists = "✅" if check_table_exists(table_name) else "❌"
            print(f"  {exists} {table_name}")
        print("=" * 50)

if __name__ == '__main__':
    create_missing_tables()
