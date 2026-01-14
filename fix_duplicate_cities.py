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
# Add more as needed
CITY_MERGES = {
    # Butwal variations
    'Butwal': ['Butwal;', 'Butwal Bazar', 'Butwal,', 'butwal', 'BUTWAL'],

    # Kathmandu variations
    'Kathmandu': ['Kathmandu;', 'Kathmandu,', 'kathmandu', 'KATHMANDU', 'KTM', 'Ktm'],

    # Pokhara variations
    'Pokhara': ['Pokhara;', 'Pokhara,', 'pokhara', 'POKHARA'],

    # Biratnagar variations
    'Biratnagar': ['Biratnagar;', 'Biratnagar,', 'biratnagar', 'BIRATNAGAR'],

    # Bharatpur variations
    'Bharatpur': ['Bharatpur;', 'Bharatpur,', 'bharatpur', 'BHARATPUR'],

    # Lalitpur variations
    'Lalitpur': ['Lalitpur;', 'Lalitpur,', 'lalitpur', 'LALITPUR', 'Patan'],

    # Bhaktapur variations
    'Bhaktapur': ['Bhaktapur;', 'Bhaktapur,', 'bhaktapur', 'BHAKTAPUR'],

    # Nepalgunj variations
    'Nepalgunj': ['Nepalgunj;', 'Nepalgunj,', 'nepalgunj', 'NEPALGUNJ', 'Nepalganj'],

    # Dharan variations
    'Dharan': ['Dharan;', 'Dharan,', 'dharan', 'DHARAN'],

    # Birgunj variations
    'Birgunj': ['Birgunj;', 'Birgunj,', 'birgunj', 'BIRGUNJ'],
}

total_merged = 0
total_doctors_updated = 0

try:
    with engine.connect() as conn:
        # First, get all cities
        result = conn.execute(text("SELECT id, name FROM cities ORDER BY name"))
        cities = {row[1]: row[0] for row in result.fetchall()}
        print(f"Found {len(cities)} cities in database\n")

        for canonical_name, variants in CITY_MERGES.items():
            # Find the canonical city ID
            canonical_id = cities.get(canonical_name)

            if not canonical_id:
                # Create the canonical city if it doesn't exist
                try:
                    trans = conn.begin()
                    conn.execute(text(
                        "INSERT INTO cities (name) VALUES (:name)"
                    ), {"name": canonical_name})
                    trans.commit()

                    result = conn.execute(text(
                        "SELECT id FROM cities WHERE name = :name"
                    ), {"name": canonical_name})
                    row = result.fetchone()
                    if row:
                        canonical_id = row[0]
                        cities[canonical_name] = canonical_id
                        print(f"Created canonical city: {canonical_name} (ID: {canonical_id})")
                except Exception as e:
                    print(f"  Error creating {canonical_name}: {e}")
                    continue

            # Process each variant
            for variant in variants:
                variant_id = cities.get(variant)

                if not variant_id:
                    continue  # Variant doesn't exist

                if variant_id == canonical_id:
                    continue  # Same city

                print(f"Merging '{variant}' (ID: {variant_id}) -> '{canonical_name}' (ID: {canonical_id})")

                try:
                    trans = conn.begin()

                    # Update doctors to point to canonical city
                    result = conn.execute(text(
                        "UPDATE doctors SET city_id = :canonical_id WHERE city_id = :variant_id"
                    ), {"canonical_id": canonical_id, "variant_id": variant_id})
                    doctors_updated = result.rowcount

                    # Update clinics if they reference cities
                    try:
                        result = conn.execute(text(
                            "UPDATE clinics SET city_id = :canonical_id WHERE city_id = :variant_id"
                        ), {"canonical_id": canonical_id, "variant_id": variant_id})
                    except:
                        pass  # clinics might not have city_id yet

                    # Delete the variant city
                    conn.execute(text(
                        "DELETE FROM cities WHERE id = :variant_id"
                    ), {"variant_id": variant_id})

                    trans.commit()

                    total_merged += 1
                    total_doctors_updated += doctors_updated
                    print(f"  Updated {doctors_updated} doctors, deleted variant city")

                    # Remove from our tracking dict
                    del cities[variant]

                except Exception as e:
                    print(f"  Error merging: {e}")
                    try:
                        trans.rollback()
                    except:
                        pass

        # Also clean up cities with trailing punctuation or extra spaces
        print(f"\n{'=' * 60}")
        print("CLEANING UP MALFORMED CITY NAMES")
        print(f"{'=' * 60}")

        result = conn.execute(text("SELECT id, name FROM cities ORDER BY name"))
        for row in result.fetchall():
            city_id, city_name = row[0], row[1]

            # Clean the name: remove trailing punctuation, extra spaces
            cleaned_name = re.sub(r'[;,]+$', '', city_name.strip())
            cleaned_name = re.sub(r'\s+', ' ', cleaned_name)

            if cleaned_name != city_name:
                print(f"Cleaning: '{city_name}' -> '{cleaned_name}'")

                try:
                    trans = conn.begin()

                    # Check if clean name already exists
                    result2 = conn.execute(text(
                        "SELECT id FROM cities WHERE name = :name AND id != :city_id"
                    ), {"name": cleaned_name, "city_id": city_id})
                    existing = result2.fetchone()

                    if existing:
                        # Merge into existing
                        existing_id = existing[0]
                        conn.execute(text(
                            "UPDATE doctors SET city_id = :existing_id WHERE city_id = :city_id"
                        ), {"existing_id": existing_id, "city_id": city_id})
                        conn.execute(text(
                            "DELETE FROM cities WHERE id = :city_id"
                        ), {"city_id": city_id})
                        print(f"  Merged into existing city ID: {existing_id}")
                        total_merged += 1
                    else:
                        # Just update the name
                        conn.execute(text(
                            "UPDATE cities SET name = :name WHERE id = :city_id"
                        ), {"name": cleaned_name, "city_id": city_id})
                        print(f"  Updated name")

                    trans.commit()
                except Exception as e:
                    print(f"  Error: {e}")
                    try:
                        trans.rollback()
                    except:
                        pass

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
