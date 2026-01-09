#!/usr/bin/env python3
"""
Verification script for database migration.
Run this BEFORE and AFTER migration to ensure data integrity.
"""

import sqlite3
import sys
from datetime import datetime

def connect_db(db_path='instance/doctors.db'):
    """Connect to the database"""
    return sqlite3.connect(db_path)

def verify_pre_migration(conn):
    """Verify database state BEFORE migration"""
    print("=" * 60)
    print("PRE-MIGRATION VERIFICATION")
    print("=" * 60)
    print()

    cursor = conn.cursor()

    # Count total doctors
    cursor.execute("SELECT COUNT(*) FROM doctors")
    total_doctors = cursor.fetchone()[0]
    print(f"✓ Total doctors: {total_doctors}")

    # Count active doctors
    cursor.execute("SELECT COUNT(*) FROM doctors WHERE is_active = 1")
    active_doctors = cursor.fetchone()[0]
    print(f"✓ Active doctors: {active_doctors}")

    # Count verified doctors
    cursor.execute("SELECT COUNT(*) FROM doctors WHERE is_verified = 1")
    verified_doctors = cursor.fetchone()[0]
    print(f"✓ Verified doctors: {verified_doctors}")

    # Count featured doctors
    cursor.execute("SELECT COUNT(*) FROM doctors WHERE is_featured = 1")
    featured_doctors = cursor.fetchone()[0]
    print(f"✓ Featured doctors: {featured_doctors}")

    # List doctors with user accounts (signed up doctors)
    cursor.execute("""
        SELECT d.id, d.name, d.email, u.email as user_email, d.phone_number
        FROM doctors d
        LEFT JOIN users u ON u.doctor_profile_id = d.id
        WHERE u.id IS NOT NULL
    """)
    signed_up_doctors = cursor.fetchall()
    print(f"\n✓ Doctors with accounts (signed up): {len(signed_up_doctors)}")
    if signed_up_doctors:
        print("\nSigned up doctors:")
        for doc in signed_up_doctors:
            print(f"  - ID: {doc[0]}, Name: {doc[1]}, Email: {doc[2]}/{doc[3]}, Phone: {doc[4]}")

    # Check for doctors with important data
    cursor.execute("""
        SELECT COUNT(*) FROM doctors
        WHERE phone_number IS NOT NULL
        OR practice_address IS NOT NULL
        OR photo_url IS NOT NULL
    """)
    doctors_with_data = cursor.fetchone()[0]
    print(f"\n✓ Doctors with contact/profile data: {doctors_with_data}")

    return {
        'total_doctors': total_doctors,
        'active_doctors': active_doctors,
        'verified_doctors': verified_doctors,
        'featured_doctors': featured_doctors,
        'signed_up_doctors': len(signed_up_doctors),
        'doctors_with_data': doctors_with_data
    }

def verify_post_migration(conn, pre_stats):
    """Verify database state AFTER migration"""
    print("\n" + "=" * 60)
    print("POST-MIGRATION VERIFICATION")
    print("=" * 60)
    print()

    cursor = conn.cursor()

    # Verify new tables exist
    cursor.execute("""
        SELECT name FROM sqlite_master
        WHERE type='table'
        AND name IN ('doctor_contact', 'doctor_subscription', 'doctor_credentials',
                     'doctor_settings', 'doctor_medical_tools', 'doctor_template_usage')
    """)
    new_tables = [row[0] for row in cursor.fetchall()]
    print(f"✓ New tables created: {len(new_tables)}/6")
    for table in new_tables:
        print(f"  - {table}")

    if len(new_tables) != 6:
        print("\n❌ ERROR: Not all tables were created!")
        return False

    # Verify data migration counts
    print("\nData migration verification:")

    tables_to_check = [
        'doctor_contact',
        'doctor_subscription',
        'doctor_credentials',
        'doctor_settings'
    ]

    all_counts_match = True
    for table in tables_to_check:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"  - {table}: {count} rows")

        if count != pre_stats['total_doctors']:
            print(f"    ❌ WARNING: Expected {pre_stats['total_doctors']} rows!")
            all_counts_match = False
        else:
            print(f"    ✓ Matches total doctors")

    # Verify signed up doctors have all their data
    cursor.execute("""
        SELECT
            d.id,
            d.name,
            dc.phone_number,
            ds.photo_url,
            dsub.subscription_tier
        FROM doctors d
        LEFT JOIN users u ON u.doctor_profile_id = d.id
        LEFT JOIN doctor_contact dc ON dc.doctor_id = d.id
        LEFT JOIN doctor_settings ds ON ds.doctor_id = d.id
        LEFT JOIN doctor_subscription dsub ON dsub.doctor_id = d.id
        WHERE u.id IS NOT NULL
    """)
    signed_up_after = cursor.fetchall()

    print(f"\n✓ Signed up doctors after migration: {len(signed_up_after)}")
    if len(signed_up_after) != pre_stats['signed_up_doctors']:
        print(f"  ❌ ERROR: Count mismatch! Before: {pre_stats['signed_up_doctors']}, After: {len(signed_up_after)}")
        return False

    print("\nSigned up doctors data verification:")
    for doc in signed_up_after:
        print(f"  - ID: {doc[0]}, Name: {doc[1]}")
        print(f"    Phone: {doc[2] or 'None'}")
        print(f"    Photo: {doc[3] or 'None'}")
        print(f"    Tier: {doc[4] or 'free'}")

    # Verify no data loss
    cursor.execute("SELECT COUNT(*) FROM doctors")
    total_after = cursor.fetchone()[0]

    if total_after != pre_stats['total_doctors']:
        print(f"\n❌ CRITICAL ERROR: Doctor count changed! Before: {pre_stats['total_doctors']}, After: {total_after}")
        return False

    print(f"\n✓ Total doctors unchanged: {total_after}")

    if all_counts_match:
        print("\n" + "=" * 60)
        print("✅ MIGRATION SUCCESSFUL - All verifications passed!")
        print("=" * 60)
        return True
    else:
        print("\n" + "=" * 60)
        print("⚠️  MIGRATION COMPLETED WITH WARNINGS")
        print("=" * 60)
        return False

def main():
    """Main verification function"""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python verify_migration.py pre   # Run before migration")
        print("  python verify_migration.py post  # Run after migration")
        sys.exit(1)

    mode = sys.argv[1].lower()
    db_path = sys.argv[2] if len(sys.argv) > 2 else 'instance/doctors.db'

    try:
        conn = connect_db(db_path)

        if mode == 'pre':
            stats = verify_pre_migration(conn)
            # Save stats for post-migration verification
            with open('migration_stats.txt', 'w') as f:
                f.write(f"timestamp={datetime.now().isoformat()}\n")
                for key, value in stats.items():
                    f.write(f"{key}={value}\n")
            print("\n✓ Stats saved to migration_stats.txt")

        elif mode == 'post':
            # Load pre-migration stats
            pre_stats = {}
            try:
                with open('migration_stats.txt', 'r') as f:
                    for line in f:
                        if '=' in line:
                            key, value = line.strip().split('=', 1)
                            if key != 'timestamp':
                                pre_stats[key] = int(value)
            except FileNotFoundError:
                print("❌ ERROR: migration_stats.txt not found. Run 'pre' verification first!")
                sys.exit(1)

            success = verify_post_migration(conn, pre_stats)
            sys.exit(0 if success else 1)

        else:
            print(f"❌ ERROR: Unknown mode '{mode}'. Use 'pre' or 'post'.")
            sys.exit(1)

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        conn.close()

if __name__ == '__main__':
    main()
