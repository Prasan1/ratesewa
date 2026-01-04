#!/usr/bin/env python3
"""
Migration: Import 24K doctors from NMC complete dataset
Run this in DigitalOcean App Platform Console after deploying code

This migration:
1. Imports all doctors from nmc_doctors_complete.csv
2. Skips existing doctors (no duplicates)
3. Cleans duplicate specializations
4. Is safe to run multiple times
"""

from app import app, db
from models import Doctor, City, Specialty, Article
import csv
import sys
from slugify import slugify


def clean_duplicate_specializations():
    """Clean up duplicate specializations"""
    print("\n" + "="*60)
    print("STEP 1: Cleaning Duplicate Specializations")
    print("="*60)

    # Mapping: duplicate_id -> primary_id
    MERGES = {
        10: 23,  # ENT Specialist -> ENT
        34: 23,  # ENT, HNS -> ENT
        2: 18,   # Cardiologist -> Cardiology
        3: 13,   # Dermatologist -> Dermatology
        1: 37,   # General Practitioner -> General Physician
        25: 37,  # General Physician | Endocrinology -> General Physician
        4: 26,   # Pediatrician -> Pediatrics
        5: 21,   # Gynecologist -> Obstetrics & Gynecology
        33: 21,  # Obs. Gynaecology -> Obstetrics & Gynecology
        8: 19,   # Psychiatrist -> Psychiatry
        24: 35,  # Urology | Andrology -> Urology
    }

    merged_count = 0
    for duplicate_id, primary_id in MERGES.items():
        duplicate = Specialty.query.get(duplicate_id)
        primary = Specialty.query.get(primary_id)

        if not duplicate or not primary:
            continue

        # Update doctors
        doctor_count = Doctor.query.filter_by(specialty_id=duplicate_id).count()
        if doctor_count > 0:
            Doctor.query.filter_by(specialty_id=duplicate_id).update({'specialty_id': primary_id})
            print(f"  ✓ Merged '{duplicate.name}' -> '{primary.name}' ({doctor_count} doctors)")
            merged_count += 1

        # Update articles that reference this specialty
        article_count = Article.query.filter_by(related_specialty_id=duplicate_id).count()
        if article_count > 0:
            Article.query.filter_by(related_specialty_id=duplicate_id).update({'related_specialty_id': primary_id})
            print(f"  ✓ Updated {article_count} articles referencing '{duplicate.name}'")

        db.session.delete(duplicate)

    # Rename for consistency
    ortho = Specialty.query.get(6)
    if ortho and ortho.name == 'Orthopedic':
        ortho.name = 'Orthopedics'
        print(f"  ✓ Renamed 'Orthopedic' -> 'Orthopedics'")

    db.session.commit()
    print(f"\n✓ Cleaned {merged_count} duplicate specializations")


def import_doctors():
    """Import doctors from CSV"""
    print("\n" + "="*60)
    print("STEP 2: Importing Doctors from nmc_doctors_complete.csv")
    print("="*60)

    csv_file = 'nmc_doctors_complete.csv'

    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)

            stats = {
                'total': 0,
                'created': 0,
                'skipped': 0,
                'invalid': 0
            }

            # Cache cities and specialties
            city_cache = {city.name.lower(): city for city in City.query.all()}
            specialty_cache = {spec.name.lower(): spec for spec in Specialty.query.all()}

            # Get General Physician for default specialty
            general_physician = Specialty.query.filter_by(name='General Physician').first()
            if not general_physician:
                general_physician = Specialty(name='General Physician')
                db.session.add(general_physician)
                db.session.flush()

            batch = []
            batch_size = 500

            for row in reader:
                stats['total'] += 1

                if stats['total'] % 1000 == 0:
                    print(f"  Processed {stats['total']:,} rows...")

                nmc_no = row.get('nmc_no', '').strip()
                name = row.get('full_name', '').strip()
                address = row.get('address', '').strip()
                degree = row.get('degree', '').strip()

                if not nmc_no or not name:
                    stats['invalid'] += 1
                    continue

                # Check if already exists
                if Doctor.query.filter_by(nmc_number=nmc_no).first():
                    stats['skipped'] += 1
                    continue

                # Extract city from address
                city_name = ''
                if address:
                    parts = [p.strip() for p in address.split(',') if p.strip()]
                    if len(parts) >= 2:
                        city_name = parts[1]
                    elif len(parts) == 1:
                        city_name = parts[0]

                if not city_name:
                    stats['invalid'] += 1
                    continue

                # Get or create city
                city_key = city_name.lower()
                if city_key not in city_cache:
                    city = City(name=city_name)
                    db.session.add(city)
                    db.session.flush()
                    city_cache[city_key] = city
                else:
                    city = city_cache[city_key]

                # Generate slug
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
                    nmc_number=nmc_no,
                    city_id=city.id,
                    specialty_id=general_physician.id,
                    education=degree or None,
                    is_verified=False,
                    is_active=True,
                    experience=0,
                    description=f"Registered doctor with Nepal Medical Council. {degree or 'Medical professional'} practicing in {city_name}."
                )

                batch.append(doctor)
                stats['created'] += 1

                # Commit in batches
                if len(batch) >= batch_size:
                    db.session.bulk_save_objects(batch)
                    db.session.commit()
                    print(f"  ✓ Committed batch. Total created: {stats['created']:,}")
                    batch = []

            # Commit remaining
            if batch:
                db.session.bulk_save_objects(batch)
                db.session.commit()

            print("\n" + "="*60)
            print("Import Summary")
            print("="*60)
            print(f"Total rows: {stats['total']:,}")
            print(f"Created: {stats['created']:,}")
            print(f"Skipped (existing): {stats['skipped']:,}")
            print(f"Invalid: {stats['invalid']:,}")
            print("="*60)

    except FileNotFoundError:
        print(f"\n❌ ERROR: {csv_file} not found!")
        print("Make sure the file is in the same directory as this script.")
        sys.exit(1)


def verify_import():
    """Verify the import results"""
    print("\n" + "="*60)
    print("STEP 3: Verification")
    print("="*60)

    total = Doctor.query.count()
    with_nmc = Doctor.query.filter(Doctor.nmc_number != None, Doctor.nmc_number != '').count()
    verified = Doctor.query.filter_by(is_verified=True).count()
    total_cities = City.query.count()
    total_specs = Specialty.query.count()

    print(f"✓ Total doctors: {total:,}")
    print(f"✓ With NMC numbers: {with_nmc:,}")
    print(f"✓ Verified: {verified:,}")
    print(f"✓ Cities: {total_cities:,}")
    print(f"✓ Specialties: {total_specs:,}")
    print("="*60)

    if total >= 20000:
        print("\n🎉 SUCCESS! Database has 20K+ doctors")
    else:
        print(f"\n⚠️  Warning: Expected 20K+ doctors, found {total:,}")


def main():
    print("\n" + "="*60)
    print("MIGRATION: Import 24K Doctors from NMC Dataset")
    print("="*60)
    print("This migration will:")
    print("  1. Clean duplicate specializations")
    print("  2. Import doctors from nmc_doctors_complete.csv")
    print("  3. Skip existing doctors (safe to re-run)")
    print("="*60)

    with app.app_context():
        try:
            clean_duplicate_specializations()
            import_doctors()
            verify_import()

            print("\n✅ Migration completed successfully!\n")

        except Exception as e:
            print(f"\n❌ ERROR during migration: {e}")
            import traceback
            traceback.print_exc()
            db.session.rollback()
            sys.exit(1)


if __name__ == '__main__':
    main()
