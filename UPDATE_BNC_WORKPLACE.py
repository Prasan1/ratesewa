#!/usr/bin/env python3
"""
Fix B&C doctors: Clear incorrect education/college, set proper workplace
"""

from app import app, db
from models import Doctor

def update_bnc_doctors():
    """Update B&C Medical College doctors - fix all fields"""

    with app.app_context():
        print("=" * 70)
        print("Fixing B&C Medical College Doctor Fields")
        print("=" * 70)

        # Find ONLY doctors with college = "B&C Medical College" (the incorrect import)
        bnc_doctors = Doctor.query.filter(
            Doctor.college == 'B&C Medical College'
        ).all()

        updated = 0

        for doctor in bnc_doctors:
            print(f"\n📝 Fixing: {doctor.name}")
            print(f"   Before - Education: {doctor.education}, College: {doctor.college}, Workplace: {doctor.workplace}")

            # Clear incorrect education (was set to specialty name)
            doctor.education = None

            # Clear incorrect college (was set to workplace)
            doctor.college = None

            # Set correct workplace
            doctor.workplace = "B&C Medical College, Birtamod"

            print(f"   After  - Education: None, College: None, Workplace: B&C Medical College, Birtamod")
            updated += 1

        try:
            db.session.commit()
            print("\n" + "=" * 70)
            print(f"✅ Update Complete!")
            print(f"   Fixed {updated} doctors")
            print(f"   - Cleared incorrect education field")
            print(f"   - Cleared incorrect college field")
            print(f"   - Set workplace to 'B&C Medical College, Birtamod'")
            print("=" * 70)

        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Error: {str(e)}")

if __name__ == '__main__':
    update_bnc_doctors()
