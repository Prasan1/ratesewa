#!/usr/bin/env python3
"""
Quick migration for local SQLite database
Adds workplace column to doctors table
"""

from app import app, db
from sqlalchemy import text

def migrate_local():
    """Add workplace column to local SQLite database"""

    with app.app_context():
        try:
            # Check if column already exists
            result = db.session.execute(text("""
                PRAGMA table_info(doctors);
            """))

            columns = [row[1] for row in result]

            if 'workplace' in columns:
                print("✅ Column 'workplace' already exists. No migration needed.")
                return

            # Add the column for SQLite
            print("Adding 'workplace' column to doctors table...")
            db.session.execute(text("""
                ALTER TABLE doctors ADD COLUMN workplace TEXT;
            """))

            db.session.commit()
            print("✅ Successfully added 'workplace' column to local database!")

        except Exception as e:
            db.session.rollback()
            print(f"❌ Error: {str(e)}")

if __name__ == '__main__':
    migrate_local()
