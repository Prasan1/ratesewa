#!/usr/bin/env python3
"""
Add missing specialties found in CSV file
Run this before importing doctors to ensure all specialties exist
"""

from app import app, db
from models import Specialty
from slugify import slugify

def add_specialty_if_not_exists(name):
    """Add specialty if it doesn't exist"""
    with app.app_context():
        # Check if specialty exists (case-insensitive)
        existing = Specialty.query.filter(Specialty.name.ilike(name)).first()

        if existing:
            print(f"  ⏭️  {name} - already exists")
            return False
        else:
            specialty = Specialty(
                name=name,
                slug=slugify(name)
            )
            db.session.add(specialty)
            print(f"  ✅ {name} - created")
            return True

def add_all_specialties():
    """Add all specialties found in the CSV"""

    # Specialties from the CSV file
    specialties = [
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

    with app.app_context():
        print("=" * 60)
        print("Adding Missing Specialties")
        print("=" * 60)

        added_count = 0
        for specialty_name in specialties:
            if add_specialty_if_not_exists(specialty_name):
                added_count += 1

        # Commit all changes
        try:
            db.session.commit()
            print("=" * 60)
            print(f"✅ Successfully added {added_count} new specialties")
            print("=" * 60)
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Error: {str(e)}")

if __name__ == '__main__':
    add_all_specialties()
