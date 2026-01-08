#!/usr/bin/env python3
"""
Migration script to add working_hours column to doctors table.

This script adds a TEXT column to store doctor working hours in JSON format.
Safe to run multiple times - checks if column exists before adding.

Usage:
    python3 add_working_hours_column.py
"""

from app import app, db
from sqlalchemy import text

def add_working_hours_column():
    """Add working_hours column to doctors table"""
    with app.app_context():
        try:
            # Check if column already exists using SQLite's PRAGMA
            result = db.session.execute(text("PRAGMA table_info(doctors)"))
            existing_columns = [row[1] for row in result]  # Column name is index 1

            if 'working_hours' in existing_columns:
                print("✅ Column 'working_hours' already exists in doctors table")
                return

            # Add working_hours column if it doesn't exist
            print("Adding 'working_hours' column...")
            db.session.execute(text("ALTER TABLE doctors ADD COLUMN working_hours TEXT"))
            db.session.commit()
            print("✅ Successfully added 'working_hours' column to doctors table")

        except Exception as e:
            db.session.rollback()
            print(f"❌ Error: {e}")
            raise

if __name__ == '__main__':
    print("=" * 60)
    print("Adding working_hours column to doctors table")
    print("=" * 60)
    add_working_hours_column()
    print("\n✅ Migration completed successfully!")
