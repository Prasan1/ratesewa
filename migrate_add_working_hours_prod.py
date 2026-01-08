#!/usr/bin/env python3
"""
PRODUCTION migration script to add working_hours column to doctors table.
PostgreSQL compatible version.

Usage:
    python3 migrate_add_working_hours_prod.py
"""

from app import app, db
from sqlalchemy import text, inspect

def add_working_hours_column():
    """Add working_hours column to doctors table (PostgreSQL)"""
    with app.app_context():
        try:
            # Use SQLAlchemy inspector (works for both SQLite and PostgreSQL)
            inspector = inspect(db.engine)
            existing_columns = [col['name'] for col in inspector.get_columns('doctors')]

            if 'working_hours' in existing_columns:
                print("✅ Column 'working_hours' already exists in doctors table")
                return

            # Add working_hours column (PostgreSQL syntax)
            print("Adding 'working_hours' column to doctors table...")
            db.session.execute(text("ALTER TABLE doctors ADD COLUMN working_hours TEXT"))
            db.session.commit()
            print("✅ Successfully added 'working_hours' column to doctors table")

        except Exception as e:
            db.session.rollback()
            print(f"❌ Error: {e}")
            raise

if __name__ == '__main__':
    print("=" * 60)
    print("PRODUCTION: Adding working_hours column to doctors table")
    print("=" * 60)
    add_working_hours_column()
    print("\n✅ Migration completed successfully!")
    print("Site should now work correctly.")
