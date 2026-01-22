#!/usr/bin/env python3
"""
Run database migrations on production.
Usage: python run_migrations.py
"""

from app import app, db
from flask_migrate import upgrade
from sqlalchemy import text, inspect

def check_table_exists(table_name):
    """Check if a table exists in the database"""
    inspector = inspect(db.engine)
    return table_name in inspector.get_table_names()

def run_migrations():
    print("=" * 50)
    print("Starting database migrations...")
    print("=" * 50)

    with app.app_context():
        # Check current state
        missing_tables = []
        tables_to_check = ['bp_records', 'sugar_records', 'medications', 'health_consents', 'patient_doctors']

        for table in tables_to_check:
            if not check_table_exists(table):
                missing_tables.append(table)

        if missing_tables:
            print(f"Missing tables: {', '.join(missing_tables)}")
        else:
            print("All health tracking tables exist.")

        print("\nRunning upgrade...")
        try:
            upgrade()
            print("\n✅ Migrations completed successfully!")

            # Verify tables were created
            still_missing = [t for t in tables_to_check if not check_table_exists(t)]
            if still_missing:
                print(f"⚠️  Still missing: {', '.join(still_missing)}")
            else:
                print("✅ All tables verified!")

        except Exception as e:
            error_msg = str(e)
            if "already exists" in error_msg:
                print(f"⚠️  Table already exists (this is OK): {e}")
            else:
                print(f"❌ Migration failed: {e}")
                raise

if __name__ == '__main__':
    run_migrations()
