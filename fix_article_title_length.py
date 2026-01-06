#!/usr/bin/env python3
"""
Migration: Increase article title length from 100 to 200 characters
"""

from app import app, db

def migrate():
    """Increase title column length for articles"""
    with app.app_context():
        print("Increasing article title length to 200 characters...")

        # Check which database we're using
        db_type = db.engine.dialect.name
        print(f"Detected database: {db_type}")

        try:
            if db_type == 'postgresql':
                # PostgreSQL syntax
                db.session.execute(db.text(
                    "ALTER TABLE articles ALTER COLUMN title TYPE VARCHAR(200);"
                ))
            elif db_type == 'sqlite':
                # SQLite doesn't support ALTER COLUMN TYPE, skip for local dev
                print("⚠ SQLite detected - ALTER COLUMN not supported")
                print("  This is OK for local dev. Run on production (PostgreSQL) to fix.")
                return

            db.session.commit()
            print("✅ Migration completed successfully!")
            print("   Article titles can now be up to 200 characters")
        except Exception as e:
            if "does not exist" in str(e).lower():
                print("⚠ Column or table doesn't exist")
            else:
                print(f"✗ Error: {e}")
                raise

if __name__ == '__main__':
    migrate()
