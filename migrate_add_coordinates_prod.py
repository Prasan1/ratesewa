#!/usr/bin/env python3
"""
Production-safe migration to add latitude/longitude to doctors table
Works for both PostgreSQL (production) and SQLite (local)
"""

from app import app, db
from sqlalchemy import text, inspect

def add_coordinate_columns():
    """Add latitude and longitude columns to doctors table"""
    with app.app_context():
        try:
            # Detect database type
            db_url = str(db.engine.url)
            is_postgres = 'postgres' in db_url

            print(f"Database type: {'PostgreSQL' if is_postgres else 'SQLite'}")

            # Check if columns already exist (works for both DB types)
            inspector = inspect(db.engine)
            existing_columns = [col['name'] for col in inspector.get_columns('doctors')]

            if 'latitude' in existing_columns and 'longitude' in existing_columns:
                print("✅ Columns 'latitude' and 'longitude' already exist in doctors table")
                return

            # Add latitude column if it doesn't exist
            if 'latitude' not in existing_columns:
                print("Adding 'latitude' column...")
                if is_postgres:
                    db.session.execute(text("ALTER TABLE doctors ADD COLUMN latitude DOUBLE PRECISION"))
                else:
                    db.session.execute(text("ALTER TABLE doctors ADD COLUMN latitude FLOAT"))
                print("✅ Added 'latitude' column")

            # Add longitude column if it doesn't exist
            if 'longitude' not in existing_columns:
                print("Adding 'longitude' column...")
                if is_postgres:
                    db.session.execute(text("ALTER TABLE doctors ADD COLUMN longitude DOUBLE PRECISION"))
                else:
                    db.session.execute(text("ALTER TABLE doctors ADD COLUMN longitude FLOAT"))
                print("✅ Added 'longitude' column")

            db.session.commit()
            print("\n🎉 Migration completed successfully!")
            print("\nNext steps:")
            print("1. Add coordinates to verified doctors via admin panel")
            print("2. Test the 'near me' feature")
            print("3. Gradually add coordinates to more doctors")

        except Exception as e:
            db.session.rollback()
            print(f"❌ Migration failed: {e}")
            raise

if __name__ == '__main__':
    print("="*60)
    print("Adding Geolocation Support to Doctors Table (Production)")
    print("="*60)
    print()
    add_coordinate_columns()
