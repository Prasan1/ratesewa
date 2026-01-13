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
        try:
            # Check if column exists
            db.session.execute(text("SELECT quick_answer FROM articles LIMIT 1"))
            print("✅ Column 'quick_answer' already exists.")
        except Exception:
            # Column doesn't exist, add it
            print("Adding 'quick_answer' column to articles table...")
            db.session.execute(text("ALTER TABLE articles ADD COLUMN quick_answer TEXT"))
            db.session.commit()
            print("✅ Column added successfully!")

if __name__ == '__main__':
    add_column()
