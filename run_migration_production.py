#!/usr/bin/env python3
"""
Production migration script for normalized doctor tables.
Run this directly with: python run_migration_production.py

Works with both SQLite (dev) and PostgreSQL (production).
"""

import sys
import os
from sqlalchemy import create_engine, text, inspect
from datetime import datetime

# Database URL from environment or default to local SQLite
DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///instance/doctors.db')

# Fix postgres:// to postgresql://
if DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

print("=" * 70)
print("DATABASE MIGRATION: Add Normalized Doctor Tables")
print("=" * 70)
print(f"\nDatabase: {DATABASE_URL.split('@')[-1] if '@' in DATABASE_URL else DATABASE_URL}")
print()

# Create engine
engine = create_engine(DATABASE_URL)
inspector = inspect(engine)

# Check if tables already exist
existing_tables = inspector.get_table_names()
new_tables = ['doctor_contact', 'doctor_subscription', 'doctor_credentials',
              'doctor_settings', 'doctor_medical_tools', 'doctor_template_usage']

tables_to_create = [t for t in new_tables if t not in existing_tables]

if not tables_to_create:
    print("✅ All tables already exist. No migration needed.")
    print("\nExisting tables:")
    for table in new_tables:
        if table in existing_tables:
            with engine.connect() as conn:
                count = conn.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
                print(f"  - {table}: {count} records")
    sys.exit(0)

print(f"Tables to create: {', '.join(tables_to_create)}")
print()

# Confirm before proceeding
response = input("Proceed with migration? (yes/no): ")
if response.lower() != 'yes':
    print("Migration cancelled.")
    sys.exit(0)

print("\nStarting migration...")

try:
    with engine.connect() as conn:
        # Start transaction
        trans = conn.begin()

        try:
            # Create doctor_contact table
            if 'doctor_contact' in tables_to_create:
                print("Creating doctor_contact table...")
                conn.execute(text("""
                    CREATE TABLE doctor_contact (
                        id SERIAL PRIMARY KEY,
                        doctor_id INTEGER NOT NULL UNIQUE REFERENCES doctors(id),
                        phone_number VARCHAR(20),
                        practice_address TEXT,
                        workplace TEXT,
                        latitude FLOAT,
                        longitude FLOAT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """))
                print("  ✓ doctor_contact created")

            # Create doctor_subscription table
            if 'doctor_subscription' in tables_to_create:
                print("Creating doctor_subscription table...")
                conn.execute(text("""
                    CREATE TABLE doctor_subscription (
                        id SERIAL PRIMARY KEY,
                        doctor_id INTEGER NOT NULL UNIQUE REFERENCES doctors(id),
                        subscription_tier VARCHAR(20) DEFAULT 'free',
                        subscription_expires_at TIMESTAMP,
                        trial_ends_at TIMESTAMP,
                        stripe_customer_id VARCHAR(255),
                        profile_views INTEGER DEFAULT 0,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """))
                print("  ✓ doctor_subscription created")

            # Create doctor_credentials table
            if 'doctor_credentials' in tables_to_create:
                print("Creating doctor_credentials table...")
                conn.execute(text("""
                    CREATE TABLE doctor_credentials (
                        id SERIAL PRIMARY KEY,
                        doctor_id INTEGER NOT NULL UNIQUE REFERENCES doctors(id),
                        nmc_number VARCHAR(50),
                        external_clinic_url TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """))
                print("  ✓ doctor_credentials created")

            # Create doctor_settings table
            if 'doctor_settings' in tables_to_create:
                print("Creating doctor_settings table...")
                conn.execute(text("""
                    CREATE TABLE doctor_settings (
                        id SERIAL PRIMARY KEY,
                        doctor_id INTEGER NOT NULL UNIQUE REFERENCES doctors(id),
                        photo_url TEXT,
                        working_hours TEXT,
                        clinic_id INTEGER REFERENCES clinics(id),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """))
                print("  ✓ doctor_settings created")

            # Create doctor_medical_tools table
            if 'doctor_medical_tools' in tables_to_create:
                print("Creating doctor_medical_tools table...")
                conn.execute(text("""
                    CREATE TABLE doctor_medical_tools (
                        id SERIAL PRIMARY KEY,
                        doctor_id INTEGER NOT NULL UNIQUE REFERENCES doctors(id),
                        signature_image TEXT,
                        clinic_letterhead TEXT,
                        default_clinic_name VARCHAR(255),
                        default_clinic_address TEXT,
                        default_consultation_fee INTEGER,
                        certificate_settings TEXT,
                        prescription_settings TEXT,
                        tools_enabled BOOLEAN DEFAULT TRUE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """))
                print("  ✓ doctor_medical_tools created")

            # Create doctor_template_usage table
            if 'doctor_template_usage' in tables_to_create:
                print("Creating doctor_template_usage table...")
                conn.execute(text("""
                    CREATE TABLE doctor_template_usage (
                        id SERIAL PRIMARY KEY,
                        doctor_id INTEGER NOT NULL REFERENCES doctors(id),
                        template_type VARCHAR(50),
                        generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        patient_name VARCHAR(100)
                    )
                """))
                print("  ✓ doctor_template_usage created")

            # Commit table creation
            trans.commit()
            print("\n✅ All tables created successfully!")

        except Exception as e:
            trans.rollback()
            print(f"\n❌ Error creating tables: {e}")
            sys.exit(1)

    # Now copy data from doctors table
    print("\nCopying data from doctors table...")

    with engine.connect() as conn:
        trans = conn.begin()

        try:
            # Get doctor count
            doctor_count = conn.execute(text("SELECT COUNT(*) FROM doctors")).scalar()
            print(f"Found {doctor_count} doctors to migrate")

            # Copy to doctor_contact
            if 'doctor_contact' in tables_to_create:
                print("Copying to doctor_contact...")
                conn.execute(text("""
                    INSERT INTO doctor_contact (doctor_id, phone_number, practice_address, workplace, latitude, longitude, created_at, updated_at)
                    SELECT id, phone_number, practice_address, workplace, latitude, longitude, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
                    FROM doctors
                """))
                count = conn.execute(text("SELECT COUNT(*) FROM doctor_contact")).scalar()
                print(f"  ✓ {count} records copied")

            # Copy to doctor_subscription
            if 'doctor_subscription' in tables_to_create:
                print("Copying to doctor_subscription...")
                conn.execute(text("""
                    INSERT INTO doctor_subscription (doctor_id, subscription_tier, subscription_expires_at, trial_ends_at, stripe_customer_id, profile_views, created_at, updated_at)
                    SELECT id, COALESCE(subscription_tier, 'free'), subscription_expires_at, trial_ends_at, stripe_customer_id, COALESCE(profile_views, 0), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
                    FROM doctors
                """))
                count = conn.execute(text("SELECT COUNT(*) FROM doctor_subscription")).scalar()
                print(f"  ✓ {count} records copied")

            # Copy to doctor_credentials
            if 'doctor_credentials' in tables_to_create:
                print("Copying to doctor_credentials...")
                conn.execute(text("""
                    INSERT INTO doctor_credentials (doctor_id, nmc_number, external_clinic_url, created_at, updated_at)
                    SELECT id, nmc_number, external_clinic_url, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
                    FROM doctors
                """))
                count = conn.execute(text("SELECT COUNT(*) FROM doctor_credentials")).scalar()
                print(f"  ✓ {count} records copied")

            # Copy to doctor_settings
            if 'doctor_settings' in tables_to_create:
                print("Copying to doctor_settings...")
                conn.execute(text("""
                    INSERT INTO doctor_settings (doctor_id, photo_url, working_hours, clinic_id, created_at, updated_at)
                    SELECT id, photo_url, working_hours, clinic_id, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
                    FROM doctors
                """))
                count = conn.execute(text("SELECT COUNT(*) FROM doctor_settings")).scalar()
                print(f"  ✓ {count} records copied")

            trans.commit()
            print("\n" + "=" * 70)
            print("✅ MIGRATION COMPLETED SUCCESSFULLY!")
            print("=" * 70)

            # Final verification
            print("\nFinal verification:")
            for table in new_tables:
                count = conn.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
                print(f"  {table}: {count} records")

        except Exception as e:
            trans.rollback()
            print(f"\n❌ Error copying data: {e}")
            sys.exit(1)

except Exception as e:
    print(f"\n❌ Migration failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
