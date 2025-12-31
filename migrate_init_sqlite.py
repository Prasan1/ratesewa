#!/usr/bin/env python3
"""Initialize SQLite schema for local testing."""

import os
from sqlalchemy import inspect

from app import app, db


def migrate_sqlite():
    """Create all tables if they do not exist."""
    with app.app_context():
        instance_path = os.path.join(os.path.dirname(__file__), 'instance')
        os.makedirs(instance_path, exist_ok=True)

        inspector = inspect(db.engine)
        existing_tables = set(inspector.get_table_names())

        if existing_tables:
            print("Existing tables:", ", ".join(sorted(existing_tables)))
        else:
            print("No tables found. Creating schema...")

        db.create_all()
        print("✅ SQLite schema ready.")

        if not existing_tables:
            print("Tip: run seed_data.py to add sample cities, specialties, and doctors.")


if __name__ == '__main__':
    migrate_sqlite()
