#!/usr/bin/env python3
"""
Import doctors with embedded data (no CSV file needed)
All doctor data is hardcoded in this script
"""

import re
from app import app, db
from models import Doctor, City, Specialty
from slugify import slugify

# Embedded doctor data from CSV
DOCTORS_DATA = [
    {"name": "Prof. Dr. Anil Kumar Jha", "specialty": "Dermatology", "experience": "30+", "education": "First Professor of Dermatology in Nepal", "additional_info": "NMC 1032; Senior Professor", "city": "Kathmandu"},
    {"name": "Dr. Mahesh Shah", "specialty": "Dermatology", "experience": "29+", "education": "Dermatologist", "additional_info": "NMC 1780; Consultant Dermatologist", "city": "Kathmandu"},
    {"name": "Prof. Dr. Sagarmani Jha", "specialty": "Dermatology", "experience": "15+", "education": "Dermatologist; Professor", "additional_info": "Senior Consultant", "city": "Kathmandu"},
    {"name": "Dr. Padma Tuladhar", "specialty": "Dermatology", "experience": "17+", "education": "Postgraduate Diploma in Dermatology; Laser Fellowship", "additional_info": "NMC 4462", "city": "Kathmandu"},
    {"name": "Dr. Megha Dev", "specialty": "Dermatology", "experience": "", "education": "Consultant Dermatologist", "additional_info": "NMC 17270", "city": "Kathmandu"},
    {"name": "Dr. Suchana Marahatta", "specialty": "Dermatology", "experience": "10+", "education": "Associate Professor", "additional_info": "Consultant Dermatologist", "city": "Kathmandu"},
    {"name": "Dr. Smita Joshi", "specialty": "Pediatric Dermatology", "experience": "", "education": "Pediatric Dermatologist", "additional_info": "", "city": "Kathmandu"},
    {"name": "Dr. Siree Thapa", "specialty": "Dermatology", "experience": "5+", "education": "Consultant Dermatologist", "additional_info": "NMC 8038", "city": "Kathmandu"},
    {"name": "Dr. Prarthana Adhikari", "specialty": "Dermatology", "experience": "", "education": "MBBS; MD Dermatology", "additional_info": "NMC 12420", "city": "Kathmandu"},
    {"name": "Prof. Dr. Shristi Shrestha", "specialty": "Dermatology", "experience": "18+", "education": "Senior Consultant Dermatologist", "additional_info": "Medical Advisor", "city": "Kathmandu"},
    {"name": "Prof. Dr. Prakash Kafle", "specialty": "Neurosurgery", "experience": "17+", "education": "MBBS; MS; MCh; FMISS", "additional_info": "Professor & HOD", "city": "Biratnagar"},
    {"name": "Dr. Ram Hari Ghimire", "specialty": "Pulmonology", "experience": "", "education": "Specialist", "additional_info": "Principal & HOD", "city": "Biratnagar"},
    {"name": "Dr. Rajesh Nepal", "specialty": "Cardiology", "experience": "10+", "education": "MD; DM", "additional_info": "Professor", "city": "Biratnagar"},
    {"name": "Dr. Vijay Kaul", "specialty": "Psychiatry", "experience": "", "education": "Associate Professor", "additional_info": "", "city": "Biratnagar"},
    {"name": "Dr. Manish Pradhan", "specialty": "Dermatology", "experience": "", "education": "MBBS; MD Dermatology", "additional_info": "Associate Professor & Head", "city": "Biratnagar"},
    {"name": "Dr. Rupak Bhattarai", "specialty": "Anesthesiology", "experience": "", "education": "MD Anesthesiology", "additional_info": "Head of Department", "city": "Biratnagar"},
    {"name": "Dr. Shanti Subedi", "specialty": "Obstetrics & Gynecology", "experience": "", "education": "Senior Gynecologist", "additional_info": "Professor", "city": "Biratnagar"},
    {"name": "Dr. Bandana Paudel", "specialty": "Anesthesiology", "experience": "", "education": "MD Anesthesiology", "additional_info": "Head of Department", "city": "Biratnagar"},
]

def parse_years_experience(experience_str):
    """Parse years of experience from strings like '30+', '15+', or empty"""
    if not experience_str or experience_str.strip() == '':
        return None
    match = re.search(r'(\d+)', experience_str)
    if match:
        return int(match.group(1))
    return None

def get_or_create_city(city_name):
    """Get existing city or create new one"""
    if not city_name:
        city_name = "Kathmandu"

    city = City.query.filter(City.name.ilike(city_name)).first()
    if not city:
        city = City(name=city_name)
        db.session.add(city)
        db.session.flush()
        print(f"  ✅ Created new city: {city_name}")
    return city

def get_specialty(specialty_name):
    """Get existing specialty"""
    if not specialty_name:
        return None

    specialty = Specialty.query.filter(Specialty.name.ilike(specialty_name)).first()

    if not specialty:
        print(f"  ⚠️  Specialty not found: {specialty_name}")
        return None

    return specialty

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
    existing = Doctor.query.filter(Doctor.name.ilike(name)).first()
    return existing is not None

def create_missing_specialties():
    """Create any missing specialties needed for import"""
    specialties_needed = [
        "Dermatology",
        "Pediatric Dermatology",
        "Neurosurgery",
        "Pulmonology",
        "Critical Care",
        "Cardiology",
        "Psychiatry",
        "Anesthesiology",
        "Obstetrics & Gynecology",
    ]

    created_count = 0
    for specialty_name in specialties_needed:
        existing = Specialty.query.filter(Specialty.name.ilike(specialty_name)).first()
        if not existing:
            specialty = Specialty(name=specialty_name)
            db.session.add(specialty)
            print(f"  ✅ Created specialty: {specialty_name}")
            created_count += 1
        else:
            print(f"  ⏭️  Specialty exists: {specialty_name}")

    if created_count > 0:
        db.session.commit()
        print(f"\n✅ Created {created_count} new specialties\n")
    else:
        print("\n✅ All required specialties already exist\n")

def import_doctors(use_app_context=True):
    """Import all embedded doctor data

    Args:
        use_app_context: If True, wrap in app.app_context().
                        Set to False when calling from a Flask route.
    """

    def _do_import():
        print("=" * 70)
        print("Importing Doctors from Embedded Data")
        print("=" * 70)

        # Step 1: Create missing specialties
        print("\nStep 1: Ensuring required specialties exist...")
        print("-" * 70)
        create_missing_specialties()

        # Step 2: Import doctors
        print("Step 2: Importing doctors...")
        print("-" * 70)

        imported_count = 0
        skipped_count = 0
        error_count = 0

        for idx, doctor_data in enumerate(DOCTORS_DATA, start=1):
            name = doctor_data['name']

            print(f"\n{idx}. Processing {name}...")

            # Check if doctor already exists
            if doctor_exists(name):
                print(f"  ⏭️  Skipped - already exists")
                skipped_count += 1
                continue

            try:
                # Get specialty
                specialty = get_specialty(doctor_data['specialty'])
                if not specialty:
                    print(f"  ❌ Error - Specialty '{doctor_data['specialty']}' not found")
                    error_count += 1
                    continue

                # Get or create city
                city = get_or_create_city(doctor_data['city'])

                # Parse experience
                years_exp = parse_years_experience(doctor_data['experience'])

                # Build description
                description_parts = []
                if doctor_data['education']:
                    description_parts.append(doctor_data['education'])
                if doctor_data['additional_info']:
                    description_parts.append(doctor_data['additional_info'])
                description = " | ".join(description_parts) if description_parts else None

                # Generate unique slug
                slug = generate_unique_slug(name)

                # Create doctor
                doctor = Doctor(
                    name=name,
                    specialty_id=specialty.id,
                    city_id=city.id,
                    description=description,
                    education=doctor_data['education'] if doctor_data['education'] else None,
                    college=None,
                    experience=years_exp,
                    photo_url=None,
                    slug=slug,
                    is_active=True  # Make sure imported doctors are active
                )

                db.session.add(doctor)
                db.session.flush()

                print(f"  ✅ Imported: {name}")
                print(f"     Specialty: {specialty.name}")
                print(f"     City: {city.name}")
                if years_exp:
                    print(f"     Experience: {years_exp} years")

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

        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Error committing changes: {str(e)}")
            print("   All changes have been rolled back.")

    # Run with or without app context
    if use_app_context:
        with app.app_context():
            _do_import()
    else:
        _do_import()

if __name__ == '__main__':
    import_doctors()
