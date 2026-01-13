#!/usr/bin/env python3
"""
Run database migrations on production (safe version).
Handles already-existing tables gracefully.
Usage: python run_migrations.py
"""

from app import app, db
from flask_migrate import upgrade, stamp
from alembic.runtime.migration import MigrationContext
from sqlalchemy import text

def get_current_revision():
    """Get current migration revision from database"""
    with db.engine.connect() as conn:
        context = MigrationContext.configure(conn)
        return context.get_current_revision()

def run_migrations():
    print("Starting database migrations...")

    with app.app_context():
        current = get_current_revision()
        print(f"Current revision: {current or 'None'}")

        # If tables exist but no migration history, stamp to latest
        if current is None:
            print("No migration history found. Checking if tables exist...")
            try:
                # Check if a known table exists
                result = db.session.execute(text("SELECT 1 FROM doctors LIMIT 1"))
                print("Tables exist. Stamping to latest revision...")
                stamp(revision='head')
                print("✅ Database stamped to head. No migrations needed.")
                return
            except Exception:
                print("Tables don't exist. Running all migrations...")

        try:
            upgrade()
            print("✅ Migrations completed successfully!")
        except Exception as e:
            error_msg = str(e)
            if "already exists" in error_msg:
                print("⚠️  Some tables already exist. Stamping to head...")
                stamp(revision='head')
                print("✅ Database stamped to head.")
            else:
                print(f"❌ Migration failed: {e}")
                raise

if __name__ == '__main__':
    run_migrations()
