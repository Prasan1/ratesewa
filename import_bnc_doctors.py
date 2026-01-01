#!/usr/bin/env python3
"""
Import doctors from B&C Medical College, Birtamod, Jhapa
Source: https://bncmedicalcollege.edu.np/doctors
"""

from app import app, db
from models import Doctor, Specialty, City
from slugify import slugify

# Doctors data from B&C Medical College
DOCTORS_DATA = [
    # Anesthesia Department
    {"name": "Dr. Raju Shrestha", "specialty": "Anesthesiologist", "city": "Birtamod"},
    {"name": "Dr. Suman Thapa", "specialty": "Anesthesiologist", "city": "Birtamod"},
    {"name": "Dr. Mukesh Kumar Chaudhary", "specialty": "Anesthesiologist", "city": "Birtamod"},
    {"name": "Dr. Amresh Kumar Singh", "specialty": "Anesthesiologist", "city": "Birtamod"},
    {"name": "Dr. Diwas Manandhar", "specialty": "Anesthesiologist", "city": "Birtamod"},
    {"name": "Dr. Puja Rouniyar", "specialty": "Anesthesiologist", "city": "Birtamod"},
    {"name": "Dr. Nisha Khadka", "specialty": "Anesthesiologist", "city": "Birtamod"},

    # Pathology Department
    {"name": "Dr. Ujwal Rai", "specialty": "Pathologist", "city": "Birtamod"},
    {"name": "Dr. Monasha Vaidhya", "specialty": "Pathologist", "city": "Birtamod"},
    {"name": "Dr. Gajendra Kumar Yadav", "specialty": "Pathologist", "city": "Birtamod"},
    {"name": "Dr. Indra Prasad Chapagain", "specialty": "Pathologist", "city": "Birtamod"},
    {"name": "Dr. Jyoti Rai", "specialty": "Pathologist", "city": "Birtamod"},

    # Pediatrics Department
    {"name": "Dr. Pragya Bharati Rimal", "specialty": "Pediatrician", "city": "Birtamod"},
    {"name": "Dr. Chandra Shekar Bhagat", "specialty": "Pediatrician", "city": "Birtamod"},
    {"name": "Dr. Rajan Jaiswal", "specialty": "Pediatrician", "city": "Birtamod"},
    {"name": "Dr. Ashraya Kadariya", "specialty": "Pediatrician", "city": "Birtamod"},
    {"name": "Dr. Sanjeev Kumar Sah", "specialty": "Pediatrician", "city": "Birtamod"},

    # Radiology Department
    {"name": "Dr. Suraj Thapaliya", "specialty": "Radiologist", "city": "Birtamod"},
    {"name": "Dr. Saujan Shrestha", "specialty": "Radiologist", "city": "Birtamod"},
    {"name": "Dr. Manmohan Bir Shrestha", "specialty": "Radiologist", "city": "Birtamod"},
    {"name": "Dr. Deepa Thapa", "specialty": "Radiologist", "city": "Birtamod"},
    {"name": "Dr. Arbindra Shah", "specialty": "Radiologist", "city": "Birtamod"},
    {"name": "Assoc. Prof. Dr. Karun Devkota", "specialty": "Radiologist", "city": "Birtamod"},
    {"name": "Prof. Dr. Umesh Kumar Sharma", "specialty": "Radiologist", "city": "Birtamod"},

    # General Surgery Department
    {"name": "Dr. Bashu Dev Baskota", "specialty": "General Surgeon", "city": "Birtamod"},
    {"name": "Dr. Deepak Pun", "specialty": "General Surgeon", "city": "Birtamod"},
    {"name": "Dr. Ajay K.C.", "specialty": "General Surgeon", "city": "Birtamod"},
    {"name": "Dr. Saroj Kumar Rajbanshi", "specialty": "General Surgeon", "city": "Birtamod"},
    {"name": "Dr. Avinesh Chaudhary", "specialty": "General Surgeon", "city": "Birtamod"},
    {"name": "Dr. Mayank Raj", "specialty": "General Surgeon", "city": "Birtamod"},
    {"name": "Dr. Keshari Shah", "specialty": "General Surgeon", "city": "Birtamod"},
]

def import_bnc_doctors():
    """Import B&C Medical College doctors"""

    with app.app_context():
        print("=" * 70)
        print("Importing B&C Medical College Doctors from Birtamod, Jhapa")
        print("=" * 70)

        imported = 0
        skipped = 0
        errors = 0

        for doctor_data in DOCTORS_DATA:
            name = doctor_data['name']

            try:
                # Check if doctor already exists
                slug = slugify(name)
                existing = Doctor.query.filter_by(slug=slug).first()

                if existing:
                    print(f"⏭️  Skipping {name} - already exists")
                    skipped += 1
                    continue

                # Get or create specialty
                specialty_name = doctor_data['specialty']
                specialty = Specialty.query.filter(
                    Specialty.name.ilike(specialty_name)
                ).first()

                if not specialty:
                    # Create new specialty
                    specialty = Specialty(name=specialty_name)
                    db.session.add(specialty)
                    db.session.flush()
                    print(f"   ✨ Created specialty: {specialty_name}")

                # Get or create city (Jhapa)
                city_name = doctor_data['city']
                city = City.query.filter(City.name.ilike(city_name)).first()

                if not city:
                    city = City(name=city_name)
                    db.session.add(city)
                    db.session.flush()
                    print(f"   ✨ Created city: {city_name}")

                # Create description
                description = f"{name} is a {specialty_name} practicing at B&C Medical College, Birtamod, Nepal."

                # Create doctor
                doctor = Doctor(
                    name=name,
                    specialty_id=specialty.id,
                    city_id=city.id,
                    description=description,
                    education=f"{specialty_name}",
                    college="B&C Medical College",
                    experience=5,  # Default experience
                    photo_url=None,
                    slug=slug,
                    is_active=True
                )

                db.session.add(doctor)
                print(f"✅ Added: {name} - {specialty_name}")
                imported += 1

            except Exception as e:
                print(f"❌ Error adding {name}: {str(e)}")
                errors += 1
                continue

        # Commit all changes
        try:
            db.session.commit()
            print("\n" + "=" * 70)
            print(f"✅ Import Complete!")
            print(f"   Imported: {imported}")
            print(f"   Skipped:  {skipped}")
            print(f"   Errors:   {errors}")
            print("=" * 70)

        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Error committing to database: {str(e)}")
            print("   All changes have been rolled back.")

if __name__ == '__main__':
    import_bnc_doctors()
