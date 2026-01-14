#!/usr/bin/env python3
"""
Fix duplicate cities by merging variants into canonical names.
Examples: "Butwal", "Butwal;", "Butwal Bazar" -> "Butwal"
"""

import os
import sys
import re
from sqlalchemy import create_engine, text

# Database URL from environment
DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///instance/doctors.db')

# Fix postgres:// to postgresql://
if DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

print("=" * 60)
print("FIXING DUPLICATE CITIES")
print("=" * 60)
print(f"Database: {DATABASE_URL.split('@')[-1] if '@' in DATABASE_URL else DATABASE_URL}\n")

engine = create_engine(DATABASE_URL)

# Define city merges: variations -> canonical name
CITY_MERGES = {
    'Butwal': ['Butwal;', 'Butwal Bazar', 'Butwal,', 'butwal', 'BUTWAL'],
    'Kathmandu': ['Kathmandu;', 'Kathmandu,', 'kathmandu', 'KATHMANDU', 'KTM', 'Ktm'],
    'Pokhara': ['Pokhara;', 'Pokhara,', 'pokhara', 'POKHARA'],
    'Biratnagar': ['Biratnagar;', 'Biratnagar,', 'biratnagar', 'BIRATNAGAR'],
    'Bharatpur': ['Bharatpur;', 'Bharatpur,', 'bharatpur', 'BHARATPUR'],
    'Lalitpur': ['Lalitpur;', 'Lalitpur,', 'lalitpur', 'LALITPUR', 'Patan'],
    'Bhaktapur': ['Bhaktapur;', 'Bhaktapur,', 'bhaktapur', 'BHAKTAPUR'],
    'Nepalgunj': ['Nepalgunj;', 'Nepalgunj,', 'nepalgunj', 'NEPALGUNJ', 'Nepalganj'],
    'Dharan': ['Dharan;', 'Dharan,', 'dharan', 'DHARAN'],
    'Birgunj': ['Birgunj;', 'Birgunj,', 'birgunj', 'BIRGUNJ'],
}

total_merged = 0
total_doctors_updated = 0

try:
    # First, get all cities
    with engine.connect() as conn:
        result = conn.execute(text("SELECT id, name FROM cities ORDER BY name"))
        cities = {row[1]: row[0] for row in result.fetchall()}
        print(f"Found {len(cities)} cities in database\n")

    # Process merges - each in its own connection/transaction
    for canonical_name, variants in CITY_MERGES.items():
        canonical_id = cities.get(canonical_name)

        if not canonical_id:
            continue  # Skip if canonical doesn't exist

        for variant in variants:
            variant_id = cities.get(variant)

            if not variant_id or variant_id == canonical_id:
                continue

            print(f"Merging '{variant}' (ID: {variant_id}) -> '{canonical_name}' (ID: {canonical_id})")

            try:
                with engine.connect() as conn:
                    # Update doctors to point to canonical city
                    result = conn.execute(text(
                        "UPDATE doctors SET city_id = :canonical_id WHERE city_id = :variant_id"
                    ), {"canonical_id": canonical_id, "variant_id": variant_id})
                    doctors_updated = result.rowcount

                    # Update clinics if they reference cities
                    try:
                        conn.execute(text(
                            "UPDATE clinics SET city_id = :canonical_id WHERE city_id = :variant_id"
                        ), {"canonical_id": canonical_id, "variant_id": variant_id})
                    except:
                        pass

                    # Delete the variant city
                    conn.execute(text(
                        "DELETE FROM cities WHERE id = :variant_id"
                    ), {"variant_id": variant_id})

                    conn.commit()

                total_merged += 1
                total_doctors_updated += doctors_updated
                print(f"  Updated {doctors_updated} doctors, deleted variant city")
                del cities[variant]

            except Exception as e:
                print(f"  Error merging: {e}")

    # Clean up cities with trailing punctuation
    print(f"\n{'=' * 60}")
    print("CLEANING UP MALFORMED CITY NAMES")
    print(f"{'=' * 60}")

    # Refresh city list
    with engine.connect() as conn:
        result = conn.execute(text("SELECT id, name FROM cities ORDER BY name"))
        all_cities = list(result.fetchall())

    for city_id, city_name in all_cities:
        cleaned_name = re.sub(r'[;,]+$', '', city_name.strip())
        cleaned_name = re.sub(r'\s+', ' ', cleaned_name)

        if cleaned_name != city_name:
            print(f"Cleaning: '{city_name}' -> '{cleaned_name}'")

            try:
                with engine.connect() as conn:
                    # Check if clean name already exists
                    result = conn.execute(text(
                        "SELECT id FROM cities WHERE name = :name AND id != :city_id"
                    ), {"name": cleaned_name, "city_id": city_id})
                    existing = result.fetchone()

                    if existing:
                        existing_id = existing[0]
                        conn.execute(text(
                            "UPDATE doctors SET city_id = :existing_id WHERE city_id = :city_id"
                        ), {"existing_id": existing_id, "city_id": city_id})
                        conn.execute(text(
                            "DELETE FROM cities WHERE id = :city_id"
                        ), {"city_id": city_id})
                        conn.commit()
                        print(f"  Merged into existing city ID: {existing_id}")
                        total_merged += 1
                    else:
                        conn.execute(text(
                            "UPDATE cities SET name = :name WHERE id = :city_id"
                        ), {"name": cleaned_name, "city_id": city_id})
                        conn.commit()
                        print(f"  Updated name")

            except Exception as e:
                print(f"  Error: {e}")

    print(f"\n{'=' * 60}")
    print("CITY CLEANUP COMPLETED!")
    print(f"{'=' * 60}")
    print(f"Cities merged: {total_merged}")
    print(f"Doctors updated: {total_doctors_updated}")

except Exception as e:
    print(f"\nCLEANUP FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
