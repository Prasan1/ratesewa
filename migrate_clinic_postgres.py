#!/usr/bin/env python3
"""
Consolidated Clinic Feature Migration for PostgreSQL
Creates all clinic-related tables and columns.

Run this on DigitalOcean Console:
    python migrate_clinic_postgres.py

This migration:
- Creates clinics table
- Adds clinic_id column to doctors table
- Creates clinic_accounts table
- Creates clinic_manager_doctors junction table
"""

import os
from app import app, db
from sqlalchemy import text

def check_table_exists(conn, table_name):
    """Check if a table exists in PostgreSQL"""
    result = conn.execute(text("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables
            WHERE table_schema = 'public'
            AND table_name = :table_name
        )
    """), {'table_name': table_name})
    return result.scalar()

def check_column_exists(conn, table_name, column_name):
    """Check if a column exists in PostgreSQL"""
    result = conn.execute(text("""
        SELECT EXISTS (
            SELECT FROM information_schema.columns
            WHERE table_name = :table_name
            AND column_name = :column_name
        )
    """), {'table_name': table_name, 'column_name': column_name})
    return result.scalar()

def migrate():
    """Run all clinic-related migrations"""
    with app.app_context():
        conn = db.session.connection()

        print("Starting clinic feature migration...")
        print("=" * 60)

        # 1. Create clinics table
        if not check_table_exists(conn, 'clinics'):
            print("\n1. Creating clinics table...")
            conn.execute(text("""
                CREATE TABLE clinics (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(200) NOT NULL,
                    slug VARCHAR(250) NOT NULL UNIQUE,
                    city_id INTEGER NOT NULL REFERENCES cities(id),
                    address TEXT,
                    phone_number VARCHAR(20),
                    description TEXT,
                    is_featured BOOLEAN DEFAULT FALSE,
                    is_active BOOLEAN DEFAULT TRUE
                )
            """))

            # Create index on slug for faster lookups
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_clinics_slug ON clinics(slug)
            """))

            print("   ✅ Clinics table created")
        else:
            print("\n1. Clinics table already exists - skipping")

        # 2. Add clinic_id to doctors table
        if not check_column_exists(conn, 'doctors', 'clinic_id'):
            print("\n2. Adding clinic_id column to doctors table...")
            conn.execute(text("""
                ALTER TABLE doctors
                ADD COLUMN clinic_id INTEGER REFERENCES clinics(id)
            """))
            print("   ✅ clinic_id column added to doctors")
        else:
            print("\n2. clinic_id column already exists in doctors - skipping")

        # 3. Create clinic_accounts table
        if not check_table_exists(conn, 'clinic_accounts'):
            print("\n3. Creating clinic_accounts table...")
            conn.execute(text("""
                CREATE TABLE clinic_accounts (
                    id SERIAL PRIMARY KEY,
                    manager_user_id INTEGER NOT NULL REFERENCES users(id),
                    name VARCHAR(200),
                    subscription_tier VARCHAR(50) DEFAULT 'clinic_starter',
                    max_doctors INTEGER DEFAULT 3,
                    subscription_expires_at TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            print("   ✅ Clinic accounts table created")
        else:
            print("\n3. Clinic accounts table already exists - skipping")

        # 4. Create clinic_manager_doctors junction table
        if not check_table_exists(conn, 'clinic_manager_doctors'):
            print("\n4. Creating clinic_manager_doctors junction table...")
            conn.execute(text("""
                CREATE TABLE clinic_manager_doctors (
                    id SERIAL PRIMARY KEY,
                    manager_user_id INTEGER NOT NULL REFERENCES users(id),
                    doctor_id INTEGER NOT NULL REFERENCES doctors(id),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(manager_user_id, doctor_id)
                )
            """))

            # Create indexes for faster joins
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_clinic_manager_doctors_manager
                ON clinic_manager_doctors(manager_user_id)
            """))
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_clinic_manager_doctors_doctor
                ON clinic_manager_doctors(doctor_id)
            """))

            print("   ✅ Clinic manager-doctors junction table created")
        else:
            print("\n4. Clinic manager-doctors table already exists - skipping")

        # Commit all changes
        db.session.commit()

        print("\n" + "=" * 60)
        print("✅ Clinic feature migration completed successfully!")
        print("\nNext steps:")
        print("1. Uncomment clinic pricing in templates/pricing.html")
        print("2. Uncomment featured clinics in templates/index.html")
        print("3. Create sample clinics via /admin/clinics/new")
        print("\nSee CLINIC_FEATURE_GUIDE.md for detailed instructions.")

if __name__ == '__main__':
    migrate()
