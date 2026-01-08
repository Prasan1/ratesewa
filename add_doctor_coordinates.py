#!/usr/bin/env python3
"""
Migration script to add latitude and longitude fields to doctors table
Run this script to update the database schema for "near me" feature
"""

from app import app, db
from sqlalchemy import text

def add_coordinate_columns():
    """Add latitude and longitude columns to doctors table"""
    with app.app_context():
        try:
            # Check if columns already exist using SQLite's PRAGMA
            result = db.session.execute(text("PRAGMA table_info(doctors)"))
            existing_columns = [row[1] for row in result]  # Column name is index 1

            if 'latitude' in existing_columns and 'longitude' in existing_columns:
                print("✅ Columns 'latitude' and 'longitude' already exist in doctors table")
                return

            # Add latitude column if it doesn't exist
            if 'latitude' not in existing_columns:
                print("Adding 'latitude' column...")
                db.session.execute(text("ALTER TABLE doctors ADD COLUMN latitude FLOAT"))
                print("✅ Added 'latitude' column")

            # Add longitude column if it doesn't exist
            if 'longitude' not in existing_columns:
                print("Adding 'longitude' column...")
                db.session.execute(text("ALTER TABLE doctors ADD COLUMN longitude FLOAT"))
                print("✅ Added 'longitude' column")

            db.session.commit()
            print("\n🎉 Migration completed successfully!")
            print("\nNext steps:")
            print("1. Test the 'near me' feature locally")
            print("2. Add coordinates to some doctors via admin panel")
            print("3. Try searching with location enabled")

        except Exception as e:
            db.session.rollback()
            print(f"❌ Migration failed: {e}")
            raise

if __name__ == '__main__':
    print("="*60)
    print("Adding Geolocation Support to Doctors Table")
    print("="*60)
    print()
    add_coordinate_columns()
