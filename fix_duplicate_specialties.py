#!/usr/bin/env python3
"""
Fix duplicate specialties - merge similar specialties into one
Example: "Dermatology" and "Dermatologist" should be the same
"""

from app import app, db
from models import Doctor, Specialty

# Map of duplicates: "new name" -> list of old names to merge
SPECIALTY_MAPPINGS = {
    "Dermatologist": ["Dermatology", "Skin Specialist"],
    "Cardiologist": ["Cardiology", "Heart Specialist"],
    "Psychiatrist": ["Psychiatry", "Mental Health"],
    "Anesthesiologist": ["Anesthesiology"],
    "Obstetrician & Gynecologist": ["Obstetrics & Gynecology", "OB/GYN", "Gynecologist"],
    "Neurosurgeon": ["Neurosurgery", "Brain Surgeon"],
    "Pulmonologist": ["Pulmonology", "Lung Specialist"],
}

def merge_specialties():
    """Merge duplicate specialties"""

    with app.app_context():
        print("=" * 70)
        print("Merging Duplicate Specialties")
        print("=" * 70)

        total_merged = 0

        for target_name, source_names in SPECIALTY_MAPPINGS.items():
            # Find or create target specialty
            target = Specialty.query.filter(Specialty.name.ilike(target_name)).first()

            if not target:
                # Check if any of the source names exist
                for source_name in source_names:
                    source = Specialty.query.filter(Specialty.name.ilike(source_name)).first()
                    if source:
                        # Rename the first found source to target
                        print(f"\n✏️  Renaming '{source.name}' (ID: {source.id}) to '{target_name}'")
                        source.name = target_name
                        target = source
                        break

                if not target:
                    print(f"\n⏭️  Skipping {target_name} - no matching specialties found")
                    continue

            # Now merge all source specialties into target
            for source_name in source_names:
                sources = Specialty.query.filter(Specialty.name.ilike(source_name)).all()

                for source in sources:
                    if source.id == target.id:
                        continue  # Skip self

                    # Move all doctors from source to target
                    doctors = Doctor.query.filter_by(specialty_id=source.id).all()

                    if doctors:
                        print(f"\n🔄 Merging '{source.name}' (ID: {source.id}) into '{target.name}' (ID: {target.id})")
                        print(f"   Moving {len(doctors)} doctors...")

                        for doctor in doctors:
                            doctor.specialty_id = target.id
                            print(f"   - {doctor.name}")

                        total_merged += len(doctors)

                        # Delete the old specialty
                        db.session.delete(source)
                        print(f"   ✅ Deleted specialty '{source.name}'")

        # Commit all changes
        try:
            db.session.commit()
            print("\n" + "=" * 70)
            print(f"✅ Successfully merged specialties!")
            print(f"   Total doctors moved: {total_merged}")
            print("=" * 70)

        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Error: {str(e)}")
            print("   All changes have been rolled back.")

if __name__ == '__main__':
    merge_specialties()
