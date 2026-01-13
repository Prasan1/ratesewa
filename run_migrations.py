#!/usr/bin/env python3
"""
Run database migrations on production.
Usage: python run_migrations.py
"""

from app import app, db
from flask_migrate import upgrade

def run_migrations():
    print("Starting database migrations...")
    with app.app_context():
        try:
            upgrade()
            print("✅ Migrations completed successfully!")
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            raise

if __name__ == '__main__':
    run_migrations()
