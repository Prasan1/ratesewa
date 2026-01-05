#!/usr/bin/env python3
"""
Add external_clinic_url column to doctors table
Allows doctors to link to external clinic profiles (e.g., ClinicOne)
"""

from app import app, db
from sqlalchemy import text

def add_external_clinic_url():
    """Add external_clinic_url column to doctors table"""

    with app.app_context():
        print("=" * 60)
        print("ADDING EXTERNAL_CLINIC_URL COLUMN TO DOCTORS TABLE")
        print("=" * 60)

        try:
            # Add column if it doesn't exist (PostgreSQL syntax)
            db.session.execute(text("""
                ALTER TABLE doctors
                ADD COLUMN IF NOT EXISTS external_clinic_url TEXT
            """))
            db.session.commit()

            print("✅ Column added successfully")
            print("=" * 60)

        except Exception as e:
            # If PostgreSQL syntax fails, try SQLite syntax
            print(f"⚠️ PostgreSQL syntax failed: {e}")
            print("Trying SQLite syntax...")

            try:
                db.session.rollback()
                # SQLite doesn't support IF NOT EXISTS, check if column exists first
                result = db.session.execute(text("PRAGMA table_info(doctors)")).fetchall()
                columns = [row[1] for row in result]

                if 'external_clinic_url' not in columns:
                    db.session.execute(text("""
                        ALTER TABLE doctors
                        ADD COLUMN external_clinic_url TEXT
                    """))
                    db.session.commit()
                    print("✅ Column added successfully (SQLite)")
                else:
                    print("✅ Column already exists")

                print("=" * 60)

            except Exception as e2:
                print(f"❌ Error: {e2}")
                db.session.rollback()
                print("=" * 60)

if __name__ == '__main__':
    add_external_clinic_url()
