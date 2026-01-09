#!/usr/bin/env python3
"""
Add missing columns to ratings table in production
This adds all the new fields for enhanced review functionality
"""

import os
import sys
from sqlalchemy import create_engine, text, inspect

# Database URL from environment
DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///instance/doctors.db')

# Fix postgres:// to postgresql://
if DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

print("Adding missing columns to ratings table...")
print(f"Database: {DATABASE_URL.split('@')[-1] if '@' in DATABASE_URL else DATABASE_URL}\n")

engine = create_engine(DATABASE_URL)

# List of columns to add (column_name, data_type, default_value)
columns_to_add = [
    ('ip_address', 'VARCHAR(45)', 'NULL'),
    ('user_agent', 'VARCHAR(255)', 'NULL'),
    ('suspicion_score', 'INTEGER', '0'),
    ('is_suspected', 'BOOLEAN', 'FALSE'),
    ('credibility_score', 'INTEGER', '0'),
    ('visit_time', 'VARCHAR(20)', 'NULL'),
    ('had_appointment', 'BOOLEAN', 'FALSE'),
    ('wait_time_minutes', 'INTEGER', 'NULL'),
    ('doctor_on_time', 'BOOLEAN', 'NULL'),
    ('visit_type', 'VARCHAR(20)', 'NULL'),
    ('visit_reason', 'VARCHAR(255)', 'NULL'),
    ('recommendation', 'VARCHAR(5)', 'NULL'),
    ('value_rating', 'INTEGER', 'NULL'),
    ('bedside_rating', 'INTEGER', 'NULL'),
    ('cleanliness_rating', 'INTEGER', 'NULL'),
]

try:
    with engine.connect() as conn:
        # Get existing columns
        inspector = inspect(engine)
        existing_columns = [col['name'] for col in inspector.get_columns('ratings')]

        print(f"Found {len(existing_columns)} existing columns in ratings table")
        print(f"Existing columns: {', '.join(existing_columns)}\n")

        added_count = 0
        skipped_count = 0

        for column_name, data_type, default in columns_to_add:
            if column_name in existing_columns:
                print(f"✓ Column '{column_name}' already exists, skipping")
                skipped_count += 1
                continue

            try:
                # Start transaction for each column
                trans = conn.begin()

                # Add the column
                if default == 'NULL':
                    sql = f"ALTER TABLE ratings ADD COLUMN {column_name} {data_type} DEFAULT {default}"
                else:
                    sql = f"ALTER TABLE ratings ADD COLUMN {column_name} {data_type} DEFAULT {default}"

                conn.execute(text(sql))
                trans.commit()

                print(f"✅ Added column: {column_name} ({data_type}, default={default})")
                added_count += 1

            except Exception as e:
                trans.rollback()
                error_msg = str(e).lower()
                if "already exists" in error_msg or "duplicate column" in error_msg:
                    print(f"✓ Column '{column_name}' already exists, skipping")
                    skipped_count += 1
                else:
                    print(f"❌ Error adding column '{column_name}': {e}")
                    sys.exit(1)

        print("\n" + "="*60)
        print("✅ Migration completed successfully!")
        print("="*60)
        print(f"Columns added: {added_count}")
        print(f"Columns skipped (already exist): {skipped_count}")
        print(f"Total columns processed: {len(columns_to_add)}")

except Exception as e:
    print(f"❌ Migration failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
