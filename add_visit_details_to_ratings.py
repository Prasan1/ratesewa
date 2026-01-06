#!/usr/bin/env python3
"""
Migration: Add visit experience details to ratings table

Adds fields to capture:
- Visit time (Morning/Afternoon/Evening)
- Whether patient had appointment
- Wait time in minutes
- Whether doctor was on time (for appointments)

These fields help patients make better decisions about when to visit
and what to expect regarding waiting times - a major pain point in Nepal.
"""

from app import app, db

def migrate():
    """Add new columns to ratings table"""
    with app.app_context():
        print("Adding visit experience columns to ratings table...")

        # Add the new columns
        migrations = [
            """
            ALTER TABLE ratings
            ADD COLUMN visit_time VARCHAR(20);
            """,
            """
            ALTER TABLE ratings
            ADD COLUMN had_appointment BOOLEAN DEFAULT FALSE;
            """,
            """
            ALTER TABLE ratings
            ADD COLUMN wait_time_minutes INTEGER;
            """,
            """
            ALTER TABLE ratings
            ADD COLUMN doctor_on_time BOOLEAN;
            """
        ]

        for migration_sql in migrations:
            try:
                db.session.execute(db.text(migration_sql))
                print(f"✓ Executed: {migration_sql.strip()[:50]}...")
            except Exception as e:
                if "duplicate column name" in str(e).lower() or "already exists" in str(e).lower():
                    print(f"⚠ Column already exists, skipping: {migration_sql.strip()[:50]}...")
                else:
                    print(f"✗ Error: {e}")
                    raise

        db.session.commit()
        print("\n✅ Migration completed successfully!")
        print("\nNew fields added to Rating model:")
        print("  - visit_time: When patient visited (Morning/Afternoon/Evening)")
        print("  - had_appointment: Whether they had an appointment")
        print("  - wait_time_minutes: How long they waited")
        print("  - doctor_on_time: Was doctor on time (for appointments)")

if __name__ == '__main__':
    migrate()
