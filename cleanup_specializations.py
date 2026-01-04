#!/usr/bin/env python3
"""
Clean up duplicate specializations and merge them.
This script:
1. Identifies duplicate specializations
2. Moves doctors from duplicate to primary specialization
3. Deletes duplicate specializations
"""

from app import app, db
from models import Specialty, Doctor

# Mapping: duplicate_id -> primary_id
MERGES = {
    # ENT: merge "ENT Specialist" and "ENT, HNS" into "ENT"
    10: 23,  # ENT Specialist -> ENT
    34: 23,  # ENT, HNS -> ENT

    # Cardiology: merge "Cardiologist" into "Cardiology"
    2: 18,   # Cardiologist -> Cardiology

    # Dermatology: merge "Dermatologist" into "Dermatology" (keep Pediatric Dermatology separate)
    3: 13,   # Dermatologist -> Dermatology

    # General Physician: merge variants
    1: 37,   # General Practitioner -> General Physician
    25: 37,  # General Physician | Endocrinology -> General Physician

    # Pediatrics: merge "Pediatrician" into "Pediatrics"
    4: 26,   # Pediatrician -> Pediatrics

    # Gynecology: merge into "Obstetrics & Gynecology"
    5: 21,   # Gynecologist -> Obstetrics & Gynecology
    33: 21,  # Obs. Gynaecology -> Obstetrics & Gynecology

    # Psychiatry: merge "Psychiatrist" into "Psychiatry"
    8: 19,   # Psychiatrist -> Psychiatry

    # Urology: merge "Urology | Andrology" into "Urology"
    24: 35,  # Urology | Andrology -> Urology
}

# Specializations to delete (bad data quality)
DELETE_IDS = [
    32,  # Contains entire doctor info instead of specialty name
]

# Rename for consistency
RENAMES = {
    6: "Orthopedics",  # Orthopedic -> Orthopedics
}


def merge_specializations():
    """Merge duplicate specializations"""
    with app.app_context():
        print("="*60)
        print("SPECIALTY CLEANUP - MERGING DUPLICATES")
        print("="*60)

        # Step 1: Merge duplicates
        for duplicate_id, primary_id in MERGES.items():
            duplicate = Specialty.query.get(duplicate_id)
            primary = Specialty.query.get(primary_id)

            if not duplicate:
                print(f"⚠ Duplicate specialty {duplicate_id} not found, skipping")
                continue

            if not primary:
                print(f"⚠ Primary specialty {primary_id} not found, skipping")
                continue

            # Count doctors with this specialty
            doctor_count = Doctor.query.filter_by(specialty_id=duplicate_id).count()

            print(f"\nMerging: '{duplicate.name}' (ID {duplicate_id}, {doctor_count} doctors)")
            print(f"    Into: '{primary.name}' (ID {primary_id})")

            if doctor_count > 0:
                # Update all doctors from duplicate to primary
                Doctor.query.filter_by(specialty_id=duplicate_id).update(
                    {'specialty_id': primary_id}
                )
                print(f"    ✓ Moved {doctor_count} doctors to '{primary.name}'")

            # Delete duplicate specialty
            db.session.delete(duplicate)
            print(f"    ✓ Deleted '{duplicate.name}'")

        # Step 2: Delete bad data
        for delete_id in DELETE_IDS:
            specialty = Specialty.query.get(delete_id)
            if not specialty:
                continue

            # Move doctors to General Physician
            doctor_count = Doctor.query.filter_by(specialty_id=delete_id).count()
            if doctor_count > 0:
                Doctor.query.filter_by(specialty_id=delete_id).update(
                    {'specialty_id': 37}  # General Physician
                )
                print(f"\n⚠ Fixed bad data: '{specialty.name[:50]}...'")
                print(f"    Moved {doctor_count} doctors to 'General Physician'")

            db.session.delete(specialty)
            print(f"    ✓ Deleted malformed specialty")

        # Step 3: Rename for consistency
        for specialty_id, new_name in RENAMES.items():
            specialty = Specialty.query.get(specialty_id)
            if specialty:
                old_name = specialty.name
                specialty.name = new_name
                print(f"\n✓ Renamed: '{old_name}' → '{new_name}'")

        # Commit all changes
        db.session.commit()

        print("\n" + "="*60)
        print("CLEANUP COMPLETE")
        print("="*60)

        # Show final statistics
        print("\nFinal Specialty List:")
        print("ID | Count | Name")
        print("---|-------|-----")
        specialties = Specialty.query.order_by(Specialty.name).all()
        for s in specialties:
            count = Doctor.query.filter_by(specialty_id=s.id).count()
            print(f"{s.id:3d} | {count:5d} | {s.name}")

        print(f"\nTotal specialties: {len(specialties)}")
        print(f"Total doctors: {Doctor.query.count()}")


if __name__ == '__main__':
    print("\nThis will merge duplicate specializations.")
    response = input("Continue? (yes/no): ")
    if response.lower() == 'yes':
        merge_specializations()
    else:
        print("Cancelled.")
