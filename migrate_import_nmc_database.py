#!/usr/bin/env python3
"""
Migration: Import 20K+ Doctors from NMC Database

This script imports doctors from the NMC SQLite database (~/Desktop/nmc.db)
with optimizations for large datasets.

Features:
- Batch processing (500 doctors at a time)
- Automatic name capitalization
- City normalization
- Duplicate detection
- Progress tracking

Run this in production console:
    python3 migrate_import_nmc_database.py
"""

import os
import sys
import sqlite3
from app import app, db
from models import Doctor, City, Specialty
from slugify import slugify

# Import our normalization functions
sys.path.insert(0, os.path.dirname(__file__))
from migrate_fix_name_capitalization import title_case_name
from migrate_normalize_cities import normalize_city_name

# Path to NMC database
NMC_DB_PATH = os.path.expanduser("~/Desktop/nmc.db")

def extract_city_from_location(location):
    """
    Extract city name from location string.
    Examples:
        "JYOTI SADAN,3/302 Puhowkl , Lalitpur" -> "Lalitpur"
        "Biratnagar , Morang," -> "Biratnagar"
        "Birgunj," -> "Birgunj"
    """
    if not location:
        return None

    # Split by comma and get the last meaningful part
    parts = [p.strip() for p in location.split(',') if p.strip()]

    if not parts:
        return None

    # Try last part first (usually the city)
    city_name = parts[-1]

    # If last part is empty or very short, try second to last
    if len(city_name) <= 2 and len(parts) > 1:
        city_name = parts[-2]

    # Normalize the city name
    return normalize_city_name(city_name) if city_name else None

def get_or_create_city(city_name, city_cache):
    """Get or create city, using cache for performance"""
    if not city_name:
        # Default to Kathmandu if no city
        city_name = "Kathmandu"

    # Normalize
    normalized_name = normalize_city_name(city_name)

    # Check cache
    cache_key = normalized_name.lower()
    if cache_key in city_cache:
        return city_cache[cache_key]

    # Check database (case-insensitive)
    city = City.query.filter(City.name.ilike(normalized_name)).first()

    if not city:
        # Create new city
        city = City(name=normalized_name)
        db.session.add(city)
        db.session.flush()

    # Cache it
    city_cache[cache_key] = city
    return city

def get_or_create_specialty(specialty_name, specialty_cache):
    """Get or create specialty, using cache for performance"""
    if not specialty_name:
        specialty_name = "General Physician"

    # Check cache
    cache_key = specialty_name.lower()
    if cache_key in specialty_cache:
        return specialty_cache[cache_key]

    # Check database (case-insensitive)
    specialty = Specialty.query.filter(Specialty.name.ilike(specialty_name)).first()

    if not specialty:
        # Create new specialty
        specialty = Specialty(name=specialty_name)
        db.session.add(specialty)
        db.session.flush()

    # Cache it
    specialty_cache[cache_key] = specialty
    return specialty

def main():
    print("=" * 70)
    print("Migration: Import 20K+ Doctors from NMC Database")
    print("=" * 70)
    print()

    # Check if NMC database exists
    if not os.path.exists(NMC_DB_PATH):
        print(f"❌ ERROR: NMC database not found at: {NMC_DB_PATH}")
        print()
        print("Please ensure the NMC database is at ~/Desktop/nmc.db")
        sys.exit(1)

    # Connect to NMC database
    print(f"📂 Reading from: {NMC_DB_PATH}")
    nmc_conn = sqlite3.connect(NMC_DB_PATH)
    nmc_cursor = nmc_conn.cursor()

    # Get total count
    nmc_cursor.execute("SELECT COUNT(*) FROM doctors")
    total_in_nmc = nmc_cursor.fetchone()[0]
    print(f"   Total doctors in NMC DB: {total_in_nmc:,}")
    print()

    with app.app_context():
        # Get current count
        before_count = Doctor.query.filter_by(is_active=True).count()
        print(f"Current doctors in database: {before_count:,}")
        print()

        # Statistics
        stats = {
            'imported': 0,
            'skipped_duplicate': 0,
            'skipped_invalid': 0,
            'cities_created': 0,
            'specialties_created': 0,
        }

        # Caches for performance
        city_cache = {}
        specialty_cache = {}
        existing_nmc_numbers = set()

        # Pre-load existing NMC numbers for duplicate detection
        print("Loading existing NMC numbers...")
        existing_doctors = Doctor.query.filter(Doctor.nmc_number.isnot(None)).all()
        for doc in existing_doctors:
            existing_nmc_numbers.add(str(doc.nmc_number))
        print(f"  Found {len(existing_nmc_numbers):,} existing NMC numbers")
        print()

        # Fetch all NMC doctors
        print("Importing doctors...")
        print("-" * 70)

        nmc_cursor.execute("SELECT full_name, nmc_number, location, gender, degree FROM doctors ORDER BY nmc_number")

        batch_count = 0
        batch_nmc_numbers = set()

        for row in nmc_cursor:
            full_name, nmc_number, location, gender, degree = row

            # Validate
            if not full_name or not nmc_number:
                stats['skipped_invalid'] += 1
                continue

            nmc_number_str = str(nmc_number)

            # Check if already exists
            if nmc_number_str in existing_nmc_numbers:
                stats['skipped_duplicate'] += 1
                continue

            # Check batch duplicates
            if nmc_number_str in batch_nmc_numbers:
                stats['skipped_duplicate'] += 1
                continue

            # Extract city from location
            city_name = extract_city_from_location(location)
            city = get_or_create_city(city_name, city_cache)

            # Get or create specialty (default to General Physician)
            specialty = get_or_create_specialty("General Physician", specialty_cache)

            # Capitalize name properly
            capitalized_name = title_case_name(full_name)

            # Generate unique slug
            base_slug = slugify(capitalized_name)
            slug = base_slug
            counter = 1
            while Doctor.query.filter_by(slug=slug).first():
                slug = f"{base_slug}-{counter}"
                counter += 1

            # Create doctor
            doctor = Doctor(
                name=capitalized_name,
                slug=slug,
                nmc_number=nmc_number_str,
                city_id=city.id,
                specialty_id=specialty.id,
                education=degree if degree else None,
                workplace=None,
                phone_number=None,
                is_verified=False,
                is_active=True,
                experience=0
            )

            db.session.add(doctor)
            batch_nmc_numbers.add(nmc_number_str)
            stats['imported'] += 1

            # Commit every 500 doctors
            if stats['imported'] % 500 == 0:
                db.session.commit()
                batch_nmc_numbers = set()
                print(f"  Imported {stats['imported']:,} / {total_in_nmc:,} doctors... ({stats['imported']/total_in_nmc*100:.1f}%)")

        # Final commit
        db.session.commit()

        # Close NMC database
        nmc_conn.close()

        # Final count
        after_count = Doctor.query.filter_by(is_active=True).count()

        print()
        print("=" * 70)
        print("Migration Complete!")
        print("=" * 70)
        print(f"Doctors before:        {before_count:,}")
        print(f"Doctors after:         {after_count:,}")
        print(f"Doctors imported:      {stats['imported']:,}")
        print(f"Skipped (duplicates):  {stats['skipped_duplicate']:,}")
        print(f"Skipped (invalid):     {stats['skipped_invalid']:,}")
        print()
        print(f"🎉 Your database now has {after_count:,} doctors!")
        print()

if __name__ == '__main__':
    main()
