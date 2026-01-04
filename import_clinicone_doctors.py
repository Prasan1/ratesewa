#!/usr/bin/env python3
"""
Import Clinic One doctors into RankSewa database.

This imports doctors scraped from https://clinicone.com.np/doctors-list/
Includes phone numbers, schedules, and online consultation flags.
"""

import csv
import sys
from app import app, db
from models import Doctor, City, Specialty
from slugify import slugify

def get_or_create_city(name):
    """Get existing city or create new one"""
    if not name or name.strip() == '':
        # Default to Kathmandu if no city specified
        name = 'Kathmandu'

    city = City.query.filter_by(name=name).first()
    if not city:
        city = City(name=name)
        db.session.add(city)
        db.session.flush()
        print(f"  ✓ Created city: {name}")
    return city

def get_or_create_specialty(name):
    """Get existing specialty or create new one"""
    if not name or name.strip() == '':
        name = 'General Physician'

    # Try exact match first
    specialty = Specialty.query.filter_by(name=name).first()
    if specialty:
        return specialty

    # Try case-insensitive match
    specialty = Specialty.query.filter(Specialty.name.ilike(name)).first()
    if specialty:
        return specialty

    # Create new specialty
    specialty = Specialty(name=name)
    db.session.add(specialty)
    db.session.flush()
    print(f"  ✓ Created specialty: {name}")
    return specialty

def doctor_exists(nmc_number, name):
    """Check if doctor already exists"""
    if nmc_number and nmc_number.strip():
        if Doctor.query.filter_by(nmc_number=nmc_number).first():
            return True

    # Check by name (case-insensitive)
    if Doctor.query.filter(Doctor.name.ilike(name)).first():
        return True

    return False

def generate_unique_slug(name):
    """Generate unique slug for doctor"""
    base_slug = slugify(name)
    slug = base_slug
    counter = 1

    while Doctor.query.filter_by(slug=slug).first():
        slug = f"{base_slug}-{counter}"
        counter += 1

    return slug

def import_clinicone_doctors(csv_file):
    """Import doctors from Clinic One CSV"""
    print(f"\n{'='*60}")
    print("Clinic One Doctor Import")
    print(f"{'='*60}\n")
    print(f"Source: {csv_file}\n")

    stats = {
        'total': 0,
        'imported': 0,
        'skipped_exists': 0,
        'skipped_invalid': 0,
        'cities_created': 0,
        'specialties_created': 0
    }

    with app.app_context():
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)

            for row in reader:
                stats['total'] += 1

                name = row['name'].strip()
                nmc_number = row['nmc_number'].strip()

                # Skip if no name
                if not name:
                    stats['skipped_invalid'] += 1
                    print(f"  ⚠ Row {stats['total']}: Missing name")
                    continue

                # Skip non-doctors (e.g., "Counseling Psychologist")
                if not name.startswith('Dr.'):
                    stats['skipped_invalid'] += 1
                    print(f"  ⚠ Skipping non-doctor: {name}")
                    continue

                # Check if exists
                if doctor_exists(nmc_number, name):
                    stats['skipped_exists'] += 1
                    print(f"  ⊘ Already exists: {name}")
                    continue

                # Get or create city
                city_name = row['city'].strip() if row['city'].strip() else 'Kathmandu'
                city = get_or_create_city(city_name)

                # Get or create specialty
                specialty_name = row['specialty'].strip() if row['specialty'].strip() else 'General Physician'
                specialty = get_or_create_specialty(specialty_name)

                # Generate slug
                slug = generate_unique_slug(name)

                # Create doctor (note: email field doesn't exist in Doctor model)
                doctor = Doctor(
                    name=name,
                    slug=slug,
                    nmc_number=nmc_number if nmc_number else None,
                    city_id=city.id,
                    specialty_id=specialty.id,
                    education=row['qualifications'].strip() if row['qualifications'].strip() else None,
                    workplace=row['workplace'].strip() if row['workplace'].strip() else None,
                    phone_number=row['phone'].strip() if row['phone'].strip() else None,
                    is_verified=False,  # Not self-verified yet
                    is_active=True,
                    experience=0
                )

                db.session.add(doctor)
                stats['imported'] += 1
                print(f"  ✓ Imported: {name} ({specialty_name}, {city_name})")

        # Commit all changes
        db.session.commit()
        print(f"\n{'='*60}")
        print("Import Complete!")
        print(f"{'='*60}")
        print(f"Total rows:          {stats['total']}")
        print(f"Imported:            {stats['imported']}")
        print(f"Skipped (exists):    {stats['skipped_exists']}")
        print(f"Skipped (invalid):   {stats['skipped_invalid']}")
        print(f"{'='*60}\n")

        # Show total doctors now
        total_doctors = Doctor.query.filter_by(is_active=True).count()
        print(f"🎉 Total active doctors in database: {total_doctors}\n")

if __name__ == '__main__':
    csv_file = '/home/ppaudyal/Documents/scraper/clinicone_doctors_clean.csv'
    import_clinicone_doctors(csv_file)
