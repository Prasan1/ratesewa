#!/usr/bin/env python3
"""
Migration script to add audit columns to doctors table.

Adds:
- updated_at: Timestamp of last update
- updated_by_user_id: User ID of who made the last edit

Run on DigitalOcean console:
    python add_doctor_audit_columns.py
"""

import os
import psycopg2

DATABASE_URL = os.environ.get('DATABASE_URL')

if not DATABASE_URL:
    print("ERROR: DATABASE_URL not set")
    print("This script should be run on the DigitalOcean App Console")
    exit(1)

def migrate():
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()

    # Check if columns already exist
    cur.execute("""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name = 'doctors' AND column_name IN ('updated_at', 'updated_by_user_id')
    """)
    existing = [row[0] for row in cur.fetchall()]

    if 'updated_at' not in existing:
        print("Adding 'updated_at' column to doctors table...")
        cur.execute("""
            ALTER TABLE doctors
            ADD COLUMN updated_at TIMESTAMP DEFAULT NOW()
        """)
        print("  ✓ updated_at column added")
    else:
        print("  - updated_at column already exists")

    if 'updated_by_user_id' not in existing:
        print("Adding 'updated_by_user_id' column to doctors table...")
        cur.execute("""
            ALTER TABLE doctors
            ADD COLUMN updated_by_user_id INTEGER REFERENCES users(id)
        """)
        print("  ✓ updated_by_user_id column added")
    else:
        print("  - updated_by_user_id column already exists")

    conn.commit()
    conn.close()

    print("\n✅ Migration complete!")
    print("\nNow all doctor profile edits will be tracked with:")
    print("  - updated_at: When the edit was made")
    print("  - updated_by_user_id: Who made the edit")
    print("\nAdmin edits are also logged to security_events table with event_type 'admin_doctor_edit'")

if __name__ == '__main__':
    migrate()
