#!/usr/bin/env python3
"""
Add external_clinic_url column to doctors table
Allows doctors to link to external clinic profiles (e.g., ClinicOne)
"""

from app import app, db

def add_external_clinic_url():
    """Add external_clinic_url column to doctors table"""

    with app.app_context():
        print("=" * 60)
        print("ADDING EXTERNAL_CLINIC_URL COLUMN TO DOCTORS TABLE")
        print("=" * 60)

        try:
            # Add column if it doesn't exist
            db.session.execute("""
                ALTER TABLE doctors
                ADD COLUMN IF NOT EXISTS external_clinic_url TEXT
            """)
            db.session.commit()

            print("✅ Column added successfully")
            print("=" * 60)

        except Exception as e:
            print(f"❌ Error: {e}")
            db.session.rollback()
            print("=" * 60)

if __name__ == '__main__':
    add_external_clinic_url()
