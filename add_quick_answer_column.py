#!/usr/bin/env python3
"""
Add quick_answer column to articles table if it doesn't exist.
Safe to run multiple times.
Usage: python add_quick_answer_column.py
"""

from app import app, db
from sqlalchemy import text

def add_column():
    with app.app_context():
        # Rollback any failed transaction first
        db.session.rollback()

        try:
            # Check if column exists
            result = db.session.execute(text("SELECT quick_answer FROM articles LIMIT 1"))
            db.session.rollback()  # Clean up
            print("✅ Column 'quick_answer' already exists.")
        except Exception as e:
            db.session.rollback()  # Rollback failed SELECT

            if "does not exist" in str(e) or "no such column" in str(e).lower():
                # Column doesn't exist, add it
                print("Adding 'quick_answer' column to articles table...")
                try:
                    db.session.execute(text("ALTER TABLE articles ADD COLUMN quick_answer TEXT"))
                    db.session.commit()
                    print("✅ Column added successfully!")
                except Exception as e2:
                    db.session.rollback()
                    if "already exists" in str(e2) or "duplicate column" in str(e2).lower():
                        print("✅ Column already exists.")
                    else:
                        print(f"❌ Error: {e2}")
            else:
                print(f"✅ Column check passed (might already exist)")

if __name__ == '__main__':
    add_column()
