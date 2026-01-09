#!/usr/bin/env python3
"""
Add all missing columns to production database
Fixes both users and ratings tables
"""

import os
import sys
from sqlalchemy import create_engine, text, inspect

# Database URL from environment
DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///instance/doctors.db')

# Fix postgres:// to postgresql://
if DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

print("="*60)
print("FIXING ALL MISSING COLUMNS IN PRODUCTION DATABASE")
print("="*60)
print(f"Database: {DATABASE_URL.split('@')[-1] if '@' in DATABASE_URL else DATABASE_URL}\n")

engine = create_engine(DATABASE_URL)

# Define all missing columns for each table
migrations = {
    'users': [
        ('created_at', 'TIMESTAMP', 'CURRENT_TIMESTAMP'),
        ('email_verified', 'BOOLEAN', 'FALSE'),
        ('is_admin', 'BOOLEAN', 'FALSE'),
        ('is_active', 'BOOLEAN', 'TRUE'),
        ('role', "VARCHAR(20)", "'patient'"),
        ('doctor_id', 'INTEGER', 'NULL'),
        ('points', 'INTEGER', '0'),
    ],
    'ratings': [
        ('created_at', 'TIMESTAMP', 'CURRENT_TIMESTAMP'),
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
}

total_added = 0
total_skipped = 0
total_errors = 0

try:
    inspector = inspect(engine)

    for table_name, columns_to_add in migrations.items():
        print(f"\n{'='*60}")
        print(f"TABLE: {table_name}")
        print(f"{'='*60}")

        # Get existing columns
        try:
            existing_columns = [col['name'] for col in inspector.get_columns(table_name)]
            print(f"Found {len(existing_columns)} existing columns")
            print(f"Columns to process: {len(columns_to_add)}\n")
        except Exception as e:
            print(f"❌ Error inspecting table '{table_name}': {e}")
            total_errors += 1
            continue

        table_added = 0
        table_skipped = 0

        for column_name, data_type, default in columns_to_add:
            if column_name in existing_columns:
                print(f"  ✓ {column_name:<25} (already exists)")
                table_skipped += 1
                total_skipped += 1
                continue

            try:
                with engine.connect() as conn:
                    trans = conn.begin()

                    # Build ALTER TABLE statement
                    # Handle special cases for default values
                    if default == 'NULL':
                        sql = f"ALTER TABLE {table_name} ADD COLUMN {column_name} {data_type} DEFAULT {default}"
                    elif default == 'CURRENT_TIMESTAMP':
                        sql = f"ALTER TABLE {table_name} ADD COLUMN {column_name} {data_type} DEFAULT {default}"
                    elif default.startswith("'") and default.endswith("'"):
                        # String literal already quoted
                        sql = f"ALTER TABLE {table_name} ADD COLUMN {column_name} {data_type} DEFAULT {default}"
                    else:
                        # Numeric or boolean default
                        sql = f"ALTER TABLE {table_name} ADD COLUMN {column_name} {data_type} DEFAULT {default}"

                    conn.execute(text(sql))
                    trans.commit()

                print(f"  ✅ {column_name:<25} ({data_type}, default={default})")
                table_added += 1
                total_added += 1

            except Exception as e:
                error_msg = str(e).lower()
                if "already exists" in error_msg or "duplicate column" in error_msg:
                    print(f"  ✓ {column_name:<25} (already exists)")
                    table_skipped += 1
                    total_skipped += 1
                else:
                    print(f"  ❌ {column_name:<25} ERROR: {e}")
                    total_errors += 1

        print(f"\nTable '{table_name}' summary:")
        print(f"  Added: {table_added}")
        print(f"  Skipped: {table_skipped}")

    # Final summary
    print("\n" + "="*60)
    print("✅ MIGRATION COMPLETED!")
    print("="*60)
    print(f"Total columns added: {total_added}")
    print(f"Total columns skipped: {total_skipped}")
    print(f"Total errors: {total_errors}")

    if total_errors > 0:
        print("\n⚠️  Some columns failed to add. Review errors above.")
        sys.exit(1)
    else:
        print("\n🎉 All migrations successful! Your app should work now.")

except Exception as e:
    print(f"\n❌ MIGRATION FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
