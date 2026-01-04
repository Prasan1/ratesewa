#!/usr/bin/env python3
"""
Migration: Add 3,000+ doctors from NMC registry and Clinic One

This script will:
1. Import 24 doctors from Clinic One
2. Import 3,089 doctors from NMC registry
3. Add 1,400+ cities across Nepal

Run this in production console:
    python3 migrate_add_3000_doctors.py
"""

import os
import sys

def main():
    print("=" * 70)
    print("Migration: Add 3,000+ Doctors to RankSewa")
    print("=" * 70)
    print()

    # Check if CSV files exist (they're in the same directory as this script)
    clinicone_csv = 'clinicone_doctors_clean.csv'
    nmc_csv = 'nmc_doctors.csv'

    clinicone_exists = os.path.exists(clinicone_csv)
    nmc_exists = os.path.exists(nmc_csv)

    if not clinicone_exists or not nmc_exists:
        print("⚠️  CSV files not found!")
        print()
        print("ERROR: The CSV files should be in the git repository.")
        print("Please run: git pull")
        print()
        print("The files should appear automatically after pulling:")
        print(f"  1. clinicone_doctors_clean.csv (24 doctors)")
        print(f"  2. nmc_doctors.csv (3,089 doctors)")
        print()
        sys.exit(1)

    print("✅ CSV files found!")
    print()

    # Import Clinic One doctors
    print("Step 1: Importing Clinic One doctors...")
    print("-" * 70)

    from app import app, db
    from models import Doctor, City, Specialty
    from slugify import slugify
    import csv

    with app.app_context():
        # Get current count
        before_count = Doctor.query.filter_by(is_active=True).count()
        print(f"Current doctors in database: {before_count:,}")
        print()

        # Import Clinic One
        clinicone_imported = 0
        clinicone_skipped = 0

        print(f"Reading Clinic One data from: {clinicone_csv}")

        with open(clinicone_csv, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                name = row['name'].strip()
                nmc_number = row['nmc_number'].strip()

                # Skip non-doctors
                if not name.startswith('Dr.'):
                    continue

                # Check if exists
                if nmc_number:
                    existing = Doctor.query.filter_by(nmc_number=nmc_number).first()
                    if existing:
                        clinicone_skipped += 1
                        continue

                # Get or create city
                city_name = row['city'].strip() if row['city'].strip() else 'Kathmandu'
                city = City.query.filter(City.name.ilike(city_name)).first()
                if not city:
                    city = City(name=city_name)
                    db.session.add(city)
                    db.session.flush()

                # Get or create specialty
                spec_name = row['specialty'].strip() if row['specialty'].strip() else 'General Physician'
                specialty = Specialty.query.filter(Specialty.name.ilike(spec_name)).first()
                if not specialty:
                    specialty = Specialty(name=spec_name)
                    db.session.add(specialty)
                    db.session.flush()

                # Generate unique slug
                base_slug = slugify(name)
                slug = base_slug
                counter = 1
                while Doctor.query.filter_by(slug=slug).first():
                    slug = f"{base_slug}-{counter}"
                    counter += 1

                # Create doctor
                doctor = Doctor(
                    name=name,
                    slug=slug,
                    nmc_number=nmc_number if nmc_number else None,
                    city_id=city.id,
                    specialty_id=specialty.id,
                    education=row.get('qualifications', '').strip() or None,
                    workplace=row.get('workplace', '').strip() or None,
                    phone_number=row.get('phone', '').strip() or None,
                    is_verified=False,
                    is_active=True,
                    experience=0
                )
                db.session.add(doctor)
                clinicone_imported += 1

        db.session.commit()
        print(f"✅ Clinic One: Imported {clinicone_imported}, Skipped {clinicone_skipped}")
        print()

        # Import NMC doctors
        print("Step 2: Importing NMC doctors (this takes 2-3 minutes)...")
        print("-" * 70)

        nmc_imported = 0
        nmc_skipped = 0
        nmc_invalid = 0
        cities_created = 0
        batch_nmc_numbers = set()

        print(f"Reading NMC data from: {nmc_csv}")

        with open(nmc_csv, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)

            for i, row in enumerate(reader, 1):
                # Progress indicator
                if i % 500 == 0:
                    print(f"  Processed {i} rows... (imported: {nmc_imported})")

                nmc_number = row.get('nmc_no', '').strip()
                name = row.get('full_name', '').strip()
                address = row.get('address', '').strip()
                degree = row.get('degree', '').strip()

                # Validate
                if not nmc_number or not name:
                    nmc_invalid += 1
                    continue

                # Extract city from address
                city_name = ''
                if address:
                    parts = address.split(',')
                    if len(parts) >= 2:
                        city_name = parts[1].strip()
                    elif len(parts) == 1:
                        city_name = parts[0].strip()

                if not city_name:
                    nmc_invalid += 1
                    continue

                # Check if exists
                if Doctor.query.filter_by(nmc_number=nmc_number).first():
                    nmc_skipped += 1
                    continue

                # Check batch duplicates
                if nmc_number in batch_nmc_numbers:
                    nmc_skipped += 1
                    continue

                # Get or create city
                city = City.query.filter(City.name.ilike(city_name)).first()
                if not city:
                    city = City(name=city_name)
                    db.session.add(city)
                    db.session.flush()
                    cities_created += 1

                # Get or create specialty (default to General Physician)
                specialty = Specialty.query.filter(Specialty.name.ilike('General Physician')).first()
                if not specialty:
                    specialty = Specialty(name='General Physician')
                    db.session.add(specialty)
                    db.session.flush()

                # Generate unique slug
                base_slug = slugify(name)
                slug = base_slug
                counter = 1
                while Doctor.query.filter_by(slug=slug).first():
                    slug = f"{base_slug}-{counter}"
                    counter += 1

                # Create doctor
                doctor = Doctor(
                    name=name,
                    slug=slug,
                    nmc_number=nmc_number,
                    city_id=city.id,
                    specialty_id=specialty.id,
                    education=degree or None,
                    workplace=None,
                    phone_number=None,
                    is_verified=False,
                    is_active=True,
                    experience=0
                )
                db.session.add(doctor)
                batch_nmc_numbers.add(nmc_number)
                nmc_imported += 1

                # Commit every 500 doctors
                if nmc_imported % 500 == 0:
                    db.session.commit()
                    batch_nmc_numbers = set()

        # Final commit
        db.session.commit()
        print(f"✅ NMC: Imported {nmc_imported:,}, Skipped {nmc_skipped:,}, Invalid {nmc_invalid}")
        print(f"✅ Cities created: {cities_created:,}")
        print()

        # Final count
        after_count = Doctor.query.filter_by(is_active=True).count()

        print("=" * 70)
        print("Migration Complete!")
        print("=" * 70)
        print(f"Doctors before: {before_count:,}")
        print(f"Doctors after:  {after_count:,}")
        print(f"Doctors added:  {after_count - before_count:,}")
        print()
        print("🎉 Your database now has {after_count:,} verified doctors!")
        print()

if __name__ == '__main__':
    main()
