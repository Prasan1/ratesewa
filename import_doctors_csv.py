#!/usr/bin/env python3
"""
Import doctors from CSV file
Handles bulk import with data validation, duplicate detection, and city/specialty matching
"""

import csv
import re
from app import app, db
from models import Doctor, City, Specialty
from slugify import slugify

def parse_years_experience(experience_str):
    """Parse years of experience from strings like '30+', '15+', or empty"""
    if not experience_str or experience_str.strip() == '':
        return None

    # Extract first number found
    match = re.search(r'(\d+)', experience_str)
    if match:
        return int(match.group(1))
    return None

def extract_city_name(location_str):
    """
    Extract city name from location strings like:
    - "Kathmandu / Budhanilkantha" -> "Kathmandu"
    - "Biratnagar" -> "Biratnagar"
    """
    if not location_str:
        return None

    # Split by "/" and take the first part
    parts = location_str.split('/')
    city_name = parts[0].strip()
    return city_name

def get_or_create_city(city_name):
    """Get existing city or create new one"""
    if not city_name:
        # Default to Kathmandu if no city specified
        city_name = "Kathmandu"

    # Try to find existing city (case-insensitive)
    city = City.query.filter(City.name.ilike(city_name)).first()

    if not city:
        # Create new city
        city = City(
            name=city_name
        )
        db.session.add(city)
        db.session.flush()  # Get the ID
        print(f"  ✅ Created new city: {city_name}")

    return city

def get_specialty(specialty_name):
    """Get existing specialty (case-insensitive match)"""
    if not specialty_name:
        return None

    # Try exact match first
    specialty = Specialty.query.filter(Specialty.name.ilike(specialty_name)).first()

    if specialty:
        return specialty

    # Try partial matches for common variations
    specialty_mappings = {
        'obstetrics & gynecology': ['gynecology', 'obstetrics', 'ob/gyn', 'obgyn'],
        'pediatric dermatology': ['dermatology', 'pediatrics'],
    }

    # Handle combined specialties by mapping to primary specialty
    combined_specialty_mappings = {
        'pulmonology / critical care': 'pulmonology',
        'critical care / pulmonology': 'pulmonology',
    }

    specialty_lower = specialty_name.lower()

    # Check if it's a combined specialty
    if specialty_lower in combined_specialty_mappings:
        mapped_specialty_name = combined_specialty_mappings[specialty_lower]
        specialty = Specialty.query.filter(Specialty.name.ilike(mapped_specialty_name)).first()
        if specialty:
            print(f"  ℹ️  Mapped '{specialty_name}' to '{specialty.name}'")
            return specialty

    for main_specialty, variations in specialty_mappings.items():
        for variation in variations:
            if variation in specialty_lower:
                specialty = Specialty.query.filter(Specialty.name.ilike(main_specialty)).first()
                if specialty:
                    return specialty

    print(f"  ⚠️  Specialty not found: {specialty_name}")
    return None

def generate_unique_slug(name):
    """Generate unique slug for doctor"""
    base_slug = slugify(name)
    slug = base_slug
    counter = 1

    while Doctor.query.filter_by(slug=slug).first():
        slug = f"{base_slug}-{counter}"
        counter += 1

    return slug

def doctor_exists(name):
    """Check if doctor with similar name already exists"""
    # Check exact match
    existing = Doctor.query.filter(Doctor.name.ilike(name)).first()
    return existing is not None

def import_doctors_from_csv(csv_file_path):
    """Import doctors from CSV file"""

    with app.app_context():
        print("=" * 70)
        print("Importing doctors from CSV")
        print("=" * 70)

        imported_count = 0
        skipped_count = 0
        error_count = 0

        with open(csv_file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)

            for row_num, row in enumerate(reader, start=2):  # Start at 2 (accounting for header)
                name = row.get('Name', '').strip()

                if not name:
                    print(f"Row {row_num}: Skipping - no name")
                    skipped_count += 1
                    continue

                print(f"\nRow {row_num}: Processing {name}...")

                # Check if doctor already exists
                if doctor_exists(name):
                    print(f"  ⏭️  Skipped - already exists")
                    skipped_count += 1
                    continue

                try:
                    # Extract data
                    specialty_name = row.get('Specialization', '').strip()
                    experience_str = row.get('Years of Experience', '').strip()
                    education = row.get('Education / Qualifications', '').strip()
                    additional_info = row.get('Additional Info (NMC / Roles)', '').strip()
                    location_str = row.get('Service Location', '').strip()

                    # Get specialty
                    specialty = get_specialty(specialty_name)
                    if not specialty:
                        print(f"  ❌ Error - Specialty '{specialty_name}' not found in database")
                        print(f"     Please create this specialty first or map to existing specialty")
                        error_count += 1
                        continue

                    # Get or create city
                    city_name = extract_city_name(location_str)
                    city = get_or_create_city(city_name)

                    # Parse years of experience
                    years_exp = parse_years_experience(experience_str)

                    # Build description from education and additional info
                    description_parts = []
                    if education:
                        description_parts.append(education)
                    if additional_info:
                        description_parts.append(additional_info)
                    description = " | ".join(description_parts) if description_parts else None

                    # Generate unique slug
                    slug = generate_unique_slug(name)

                    # Create doctor
                    doctor = Doctor(
                        name=name,
                        specialty_id=specialty.id,
                        city_id=city.id,
                        description=description,
                        education=education if education else None,
                        college=None,  # Not in CSV
                        experience=years_exp,
                        photo_url=None,  # No photos in CSV
                        slug=slug
                    )

                    db.session.add(doctor)
                    db.session.flush()

                    print(f"  ✅ Imported: {name}")
                    print(f"     Specialty: {specialty.name}")
                    print(f"     City: {city.name}")
                    print(f"     Experience: {years_exp} years" if years_exp else "     Experience: Not specified")

                    imported_count += 1

                except Exception as e:
                    print(f"  ❌ Error importing {name}: {str(e)}")
                    error_count += 1
                    db.session.rollback()
                    continue

        # Commit all changes
        try:
            db.session.commit()
            print("\n" + "=" * 70)
            print("Import Summary:")
            print("=" * 70)
            print(f"✅ Successfully imported: {imported_count} doctors")
            print(f"⏭️  Skipped (duplicates):  {skipped_count} doctors")
            print(f"❌ Errors:               {error_count} doctors")
            print("=" * 70)

            if error_count > 0:
                print("\n⚠️  Some doctors failed to import.")
                print("   Common issues:")
                print("   - Specialty not found in database (create it first)")
                print("   - Invalid data format")

        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Error committing changes: {str(e)}")
            print("   All changes have been rolled back.")

if __name__ == '__main__':
    csv_file = 'doctors_combined.csv'
    import_doctors_from_csv(csv_file)
