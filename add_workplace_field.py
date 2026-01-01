#!/usr/bin/env python3
"""
Migration: Add workplace field to doctors table
This adds a new column to store where doctors work (hospital/clinic)
"""

from app import app, db
from sqlalchemy import text

def add_workplace_column():
    """Add workplace column to doctors table"""

    with app.app_context():
        try:
            # Check if column already exists
            result = db.session.execute(text("""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name='doctors' AND column_name='workplace';
            """))

            if result.fetchone():
                print("✅ Column 'workplace' already exists. No migration needed.")
                return

            # Add the column
            print("Adding 'workplace' column to doctors table...")
            db.session.execute(text("""
                ALTER TABLE doctors
                ADD COLUMN workplace TEXT;
            """))

            db.session.commit()
            print("✅ Successfully added 'workplace' column!")

        except Exception as e:
            db.session.rollback()
            print(f"❌ Error: {str(e)}")

if __name__ == '__main__':
    add_workplace_column()
